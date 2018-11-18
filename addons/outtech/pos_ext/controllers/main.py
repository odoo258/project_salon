# -*- coding: utf-8 -*-
import logging
import time
from threading import Thread, Lock
from requests import ConnectionError
from odoo import api, fields, models
from decimal import Decimal
import StringIO
from odoo import http
import base64
import re, string
from escpos.serial import SerialSettings
from escpos.network import NetworkConnection

_logger = logging.getLogger(__name__)

try:
    import satcfe
    from satcomum import constantes
    from satcfe import ClienteSATLocal
    from satcfe import ClienteSATHub
    from satcfe import BibliotecaSAT
    from satcfe.entidades import Emitente
    from satcfe.entidades import InformacoesAdicionais
    from satcfe.entidades import Destinatario
    from satcfe.entidades import LocalEntrega
    from satcfe.entidades import Detalhamento
    from satcfe.entidades import ProdutoServico
    from satcfe.entidades import Imposto
    from satcfe.entidades import ICMSSN102
    from satcfe.entidades import PISSN
    from satcfe.entidades import COFINSSN
    from satcfe.entidades import MeioPagamento
    from satcfe.entidades import CFeVenda
    from satcfe.entidades import DescAcrEntr
    from satcfe.entidades import CFeCancelamento
    from satcfe.excecoes import ErroRespostaSATInvalida
    from satcfe.excecoes import ExcecaoRespostaSAT
    from satextrato import ExtratoCFeVenda
    from satextrato import ExtratoCFeCancelamento

except ImportError:
    _logger.error('Odoo module hw_l10n_br_pos depends on the satcfe module')
    # satcfe = None


TWOPLACES = Decimal(10) ** -2
FOURPLACES = Decimal(10) ** -4


def punctuation_rm(string_value):
    tmp_value = (
        re.sub('[%s]' % re.escape(string.punctuation), '', string_value or ''))
    return tmp_value


class Sat(models.Model):
    _name = 'hw.sat'
    def create_cfe_sat(self, codigo_ativacao, sat_path,
                       impressora, printer_params, assinatura, info_sat, print_connection, venda, type, chavecan='',cfe_reprint=''):
        try:
            self.codigo_ativacao = codigo_ativacao
            self.sat_path = sat_path
            self.impressora = impressora
            self.printer_params = printer_params
            self.lock = Lock()
            self.satlock = Lock()
            self.status = {'status': 'connecting', 'messages': []}
            self.print_connection = print_connection
            self.printer = self._init_printer()
            self.device = self._get_device()
            self.assinatura = assinatura
            self.status_sat()
            if type == 'send':
                try:
                    payment_lines = []
                    for p in venda.statement_ids:
                        if p.amount > 0:
                            amount = p.amount
                            for k in venda.statement_ids:
                                if k.amount < 0 and p.journal_id.sat_payment_mode == k.journal_id.sat_payment_mode:
                                    amount = p.amount + k.amount
                            plines = {'sat_payment_mode':p.journal_id.sat_payment_mode,'amount':amount,'sat_card_accrediting':1}
                            payment_lines.append(plines)
                    json = {'info_sat':info_sat,
                            'venda':venda,
                           'company':{'cnpj':venda.company_id.cnpj_cpf,
                                       'ie':venda.company_id.inscr_est,
                                       'im':venda.company_id.inscr_mun,
                                       'cnpj_software_house':venda.company_id.cnpj_software_house},
                            'client':venda.cpf_nfse or '',
                            'paymentlines':payment_lines,
                                 'orderlines':venda.lines
                            }
                    sat = self._send_cfe(json, venda)
                    # self.env['pos.order.log'].sudo().create({'pos_order_id':venda.id,'log':'Enviado com sucesso - %s' %  sat['chave_cfe']})
                    # attachment = {
                    #         'name': sat['chave_cfe'],
                    #         'datas': base64.b64encode(sat['xml']),
                    #         'datas_fname': '%s.xml' % sat['chave_cfe'],
                    #         'res_model': 'pos.order',
                    #         'res_id': venda.id,
                    #     }
                    # self.env['ir.attachment'].create(attachment)
                    return venda.sudo().write({'chave_cfe': sat['chave_cfe'],
                                               'num_sessao_cfe':sat['numSessao'],
                                               'xml_cfe_retorn':sat['xml']})
                except ErroRespostaSATInvalida as ex:
                    _logger.error('SAT Error: {0}'.format(ex))
                    return self.env['pos.order.log'].sudo().create({'pos_order_id':venda.id,'log':' %s' % ex})
                except ExcecaoRespostaSAT as ex:
                    _logger.error('SAT Error: {0}'.format(ex))
                    return self.env['pos.order.log'].sudo().create({'pos_order_id':venda.id,'log':' %s' % ex})
                except Exception as ex:
                    _logger.error('SAT Error: {0}'.format(ex))
                    return self.env['pos.order.log'].sudo().create({'pos_order_id':venda.id,'log':' %s' % ex})
            if type == 'cancel' and chavecan:
                try:
                    json = {'chaveConsulta':chavecan,
                            'doc_destinatario':False,#venda.cpf_nfse,
                            'cnpj_software_house':venda.company_id.cnpj_software_house,
                            'order_id':venda.id}
                    sat_cancel = self._cancel_cfe(json, venda)
                    venda.sudo().write({'xml_cfe_cancel':sat_cancel['xml'],'chave_cfe_can':sat_cancel['chave_cfe']})
                    return self.env['pos.order.log'].sudo().create({'pos_order_id':venda.id,'log':'Cancelado com sucesso - %s' %  sat_cancel['chave_cfe']})
                except ErroRespostaSATInvalida as ex:
                    _logger.error('SAT Error: {0}'.format(ex))
                    return self.env['pos.order.log'].sudo().create({'pos_order_id':venda.id,'log':' %s' % ex})
                except ExcecaoRespostaSAT as ex:
                    _logger.error('SAT Error: {0}'.format(ex))
                    return self.env['pos.order.log'].sudo().create({'pos_order_id':venda.id,'log':' %s' % ex})
                except Exception as ex:
                    _logger.error('SAT Error: {0}'.format(ex))
                    return self.env['pos.order.log'].sudo().create({'pos_order_id':venda.id,'log':' %s' % ex})
            if type == 'reprint':
                if venda.xml_cfe_cancel:
                    self._reprint_cfe({'canceled_order':True,'xml_cfe_venda':venda.chave_cfe,'xml_cfe_cacelada':venda.xml_cfe_cancel}, venda)
                else:
                    self._reprint_cfe({'canceled_order':False,'xml_cfe_venda':cfe_reprint,'chave':venda.chave_cfe}, venda)
            #self.conn.socket.close()
        except Exception, e:
	        _logger.warning('%s' % e)
	#if self.conn:
            #    self.conn.socket.close()
    def lockedstart(self):
        with self.lock:
            if not self.isAlive():
                self.daemon = True
                self.start()

    def get_status(self):
        self.lockedstart()
        return self.status

    def set_status(self, status, message=None):
        if status == self.status['status']:
            if message is not None and message != self.status['messages'][-1]:
                self.status['messages'].append(message)

                if status == 'error' and message:
                    _logger.error('SAT Error: '+message)
                elif status == 'disconnected' and message:
                    _logger.warning('Disconnected SAT: '+message)
        else:
            self.status['status'] = status
            if message:
                self.status['messages'] = [message]
            else:
                self.status['messages'] = []

            if status == 'error' and message:
                _logger.error('SAT Error: '+message)
            elif status == 'disconnected' and message:
                _logger.warning('Disconnected SAT: '+message)

    def _get_device(self):
        if not self.sat_path and not self.codigo_ativacao:
            self.set_status('error', 'Dados do sat incorretos')
            return None
        return ClienteSATLocal(
            BibliotecaSAT(self.sat_path),
            codigo_ativacao=self.codigo_ativacao
        )

    def status_sat(self):
        with self.satlock:
            if self.device:
                try:
                    if self.device.consultar_sat():
                        self.set_status('connected', 'Connected to SAT')
                except ErroRespostaSATInvalida as ex_sat_invalida:
                    # o equipamento retornou uma resposta que não faz sentido;
                    # loga, e lança novamente ou lida de alguma maneira
                    self.device = None
                except ExcecaoRespostaSAT as ex_resposta:
                    self.set_status('disconnected', 'SAT Not Found')
                    self.device = None
                except ConnectionError as ex_conn_error:
                    self.device = None
                except Exception as ex:
                    self.set_status('error', str(ex))
                    self.device = None

    def __prepare_send_detail_cfe(self, item):
        kwargs = {}

        if item.discount or item.discount_fixed:
            disc = Decimal((((item.price_unit * item.qty) * item.discount) / 100) + item.discount_fixed).quantize(TWOPLACES)
            kwargs['vDesc'] = disc #Decimal(((item.valor_bruto * item.discount) / 100) + item.discount_fixed).quantize(TWOPLACES)
        estimated_taxes = Decimal(item.valor_icms + item.valor_pis + item.valor_cofins).quantize(TWOPLACES) #Decimal(item['estimated_taxes'] * item['price_display']).quantize(TWOPLACES)

        detalhe = Detalhamento(
                produto=ProdutoServico(
                cProd=unicode(item.product_id.default_code),
                xProd= item.product_id.name,
                CFOP=item.product_id.cfop_sat_id.code,
                uCom=item.product_id.uom_id.name[:2],
                qCom=Decimal(item.qty).quantize(FOURPLACES),
                vUnCom=Decimal(item.price_unit).quantize(TWOPLACES),
                indRegra='A',
                NCM=punctuation_rm(item.product_id.fiscal_classification_id.code),
                **kwargs
                ),
            imposto=Imposto(
                vItem12741=estimated_taxes,
                icms=ICMSSN102(Orig=item.product_id.origin, CSOSN=item.product_id.icms_sat_csosn),#Orig=item['origin'], CSOSN='500'),
                pis=PISSN(CST='49'),
                cofins=COFINSSN(CST='49'))
        )
        detalhe.validar()
        return detalhe, estimated_taxes

    def __prepare_payment(self, json): #Todo pagamento com mais cartoes e tipo de pagamento com codigo
        kwargs = {}
        #if json['sat_card_accrediting']: #Pagos em quantas formas
         #   kwargs['cAdmC'] = json['sat_card_accrediting']

        pagamento = MeioPagamento(
            cMP=json['sat_payment_mode'], # mode de pagamento
            vMP=Decimal(json['amount']).quantize(
                TWOPLACES),
            **kwargs
        )
        pagamento.validar()
        return pagamento

    def __prepare_send_cfe(self, json):
        federal = 0
        estadual = 0
        municipal = 0
        vendedor = ''
        detalhamentos = []
        total_taxes = Decimal(0.0)
        desc = False
        disc_percent = 0
        rest = Decimal(0.00).quantize(TWOPLACES)
        subtotal_lines = 0
        desc_total = Decimal(json['venda'].discount_total).quantize(TWOPLACES)
        for item in json['orderlines']:
            # De olho no imposto
            federal = 0
            estadual = 0
            municipal = 0
            federal += (item.qty * item.price_unit) * (item.product_id.fiscal_classification_id.federal_nacional / 100)
            estadual += (item.qty * item.price_unit) * (item.product_id.fiscal_classification_id.estadual_imposto / 100)
            municipal += (item.qty * item.price_unit) * (item.product_id.fiscal_classification_id.municipal_imposto / 100)

            vendedor = item.order_id.user_id and item.order_id.user_id.name or ''
            if item.discount or item.discount_fixed:
                desc = True
            else:
                desc = False
            detalhe, estimated_taxes = self.__prepare_send_detail_cfe(item)
            if json['venda'].discount_percent > 0:
                disc = Decimal((((item.price_unit * item.qty) * json['venda'].discount_percent) / 100) + json['venda'].discount_total).quantize(TWOPLACES)
                disc_percent += disc
                if desc:
                    if detalhe.produto.vDesc:
                        disc_percent += detalhe.produto.vDesc
                        detalhe.produto.vDesc = Decimal(detalhe.produto.vDesc + disc).quantize(TWOPLACES)
                    else:
                        detalhe.produto.vDesc = disc
                else:
                    detalhe.produto.vDesc = disc
            if json['venda'].discount_total > 0:
                if desc_total > 0:
                    if desc:
                        if desc_total + detalhe.produto.vDesc > Decimal(detalhe.produto.qCom * detalhe.produto.vUnCom).quantize(TWOPLACES):
                            disc = Decimal(detalhe.produto.qCom * detalhe.produto.vUnCom).quantize(TWOPLACES)
                            desc_total -= Decimal(detalhe.produto.qCom * detalhe.produto.vUnCom).quantize(TWOPLACES)
                        else:
                            disc = Decimal(desc_total + detalhe.produto.vDesc).quantize(TWOPLACES)
                            desc_total -= disc
                    else:
                        if desc_total > Decimal(detalhe.produto.qCom * detalhe.produto.vUnCom).quantize(TWOPLACES):
                            disc = Decimal(detalhe.produto.qCom * detalhe.produto.vUnCom).quantize(TWOPLACES)
                            desc_total -= Decimal(detalhe.produto.qCom * detalhe.produto.vUnCom).quantize(TWOPLACES)
                        else:
                            disc = Decimal(desc_total).quantize(TWOPLACES)
                            desc_total -= disc
                    disc_percent += disc
                    if disc > Decimal(detalhe.produto.qCom * detalhe.produto.vUnCom).quantize(TWOPLACES):
                        rest = disc - Decimal(detalhe.produto.qCom * detalhe.produto.vUnCom).quantize(TWOPLACES)
                    else:
                        disc = disc + rest
                        rest = Decimal(0.00).quantize(TWOPLACES)
                    if desc:
                        if detalhe.produto.vDesc:
                            disc_percent += detalhe.produto.vDesc
                            detalhe.produto.vDesc = Decimal(detalhe.produto.vDesc + disc).quantize(TWOPLACES)
                        else:
                            detalhe.produto.vDesc = disc
                    else:
                        detalhe.produto.vDesc = disc
            if desc:
                subtotal_lines += Decimal(detalhe.produto.qCom * detalhe.produto.vUnCom).quantize(TWOPLACES) - Decimal(detalhe.produto.vDesc).quantize(TWOPLACES)
                disc = 0
            else:
                if json['venda'].discount_total or json['venda'].discount_percent:
                    subtotal_lines += Decimal(detalhe.produto.qCom * detalhe.produto.vUnCom).quantize(TWOPLACES) - disc
                    disc = 0
                else:
                    subtotal_lines += Decimal(detalhe.produto.qCom * detalhe.produto.vUnCom).quantize(TWOPLACES)
            detalhamentos.append(detalhe)
            total_taxes += Decimal(federal + estadual + municipal).quantize(TWOPLACES)#estimated_taxes
        if json['venda']:
            # if json['venda'].discount_percent or json['venda'].discount_total:
            #     if Decimal(json['venda'].total_discount).quantize(TWOPLACES) != disc_percent and Decimal(subtotal_lines).quantize(TWOPLACES) != Decimal(json['venda'].amount_paid).quantize(TWOPLACES):
            #         detalhamentos[-1].produto.vDesc = detalhamentos[-1].produto.vDesc + Decimal(Decimal(json['venda'].total_discount).quantize(TWOPLACES) - disc_percent).quantize(TWOPLACES)
            #         if Decimal(subtotal_lines).quantize(TWOPLACES) > Decimal(json['venda'].amount_paid).quantize(TWOPLACES):
            #             detalhamentos[-1].produto.vDesc -= Decimal(subtotal_lines).quantize(TWOPLACES) - Decimal(json['venda'].amount_paid).quantize(TWOPLACES)
            #         elif Decimal(subtotal_lines).quantize(TWOPLACES) < Decimal(json['venda'].amount_paid).quantize(TWOPLACES):
            #             detalhamentos[-1].produto.vDesc += Decimal(json['venda'].amount_paid).quantize(TWOPLACES) - Decimal(subtotal_lines).quantize(TWOPLACES)
            if Decimal(json['venda'].amount_total).quantize(TWOPLACES) != Decimal(json['venda'].amount_paid).quantize(TWOPLACES):
              detalhamentos[-1].produto.vDesc = detalhamentos[-1].produto.vDesc + (Decimal(json['venda'].amount_total).quantize(TWOPLACES) - Decimal(json['venda'].amount_paid).quantize(TWOPLACES))
            if Decimal(subtotal_lines).quantize(TWOPLACES) != Decimal(json['venda'].amount_paid).quantize(TWOPLACES) and desc or desc_total > 0 or disc_percent > 0:
                if Decimal(subtotal_lines).quantize(TWOPLACES) > Decimal(json['venda'].amount_paid).quantize(TWOPLACES):
                    if hasattr(detalhamentos[0].produto, 'vDesc'):
                        detalhamentos[0].produto.vDesc = detalhamentos[0].produto.vDesc + ((Decimal(subtotal_lines).quantize(TWOPLACES) - Decimal(json['venda'].amount_paid).quantize(TWOPLACES)))
                    else:
                        detalhamentos[0].produto.vDesc = ((Decimal(subtotal_lines).quantize(TWOPLACES) - Decimal(json['venda'].amount_paid).quantize(TWOPLACES)))
                else:
                    if hasattr(detalhamentos[0].produto, 'vDesc'):
                        detalhamentos[0].produto.vDesc = detalhamentos[0].produto.vDesc - ((Decimal(json['venda'].amount_paid).quantize(TWOPLACES) - Decimal(subtotal_lines).quantize(TWOPLACES)))
                    else:
                        detalhamentos[0].produto.vDesc = ((Decimal(json['venda'].amount_paid).quantize(TWOPLACES) - Decimal(subtotal_lines).quantize(TWOPLACES)))
            # if json['venda'].discount_total > 0:
            #     # disc = Decimal((((item.price_unit * item.qty) * json['venda'].discount_percent) / 100) + json['venda'].discount_total).quantize(TWOPLACES)
            #     # if json['venda'].discount_pencent > 0:
            #     if desc:
            #         if detalhamentos[-1].produto.vDesc:
            #             detalhamentos[-1].produto.vDesc = Decimal(float(detalhamentos[-1].produto.vDesc) + json['venda'].discount_total).quantize(TWOPLACES)
            #         else:
            #             detalhamentos[-1].produto.vDesc = Decimal(json['venda'].discount_total).quantize(TWOPLACES)
            #     else:
            #         detalhamentos[-1].produto.vDesc = Decimal(json['venda'].discount_total).quantize(TWOPLACES)


        # descontos_acrescimos_subtotal = DescAcrEntr(
        #     vDescSubtot=Decimal((((json['venda'].total_discount + json['venda'].amount_total) * json['venda'].discount_percent) / 100) + json['venda'].discount_total).quantize(TWOPLACES))
        # descontos_acrescimos_subtotal.validar()

        pagamentos = []
        for pagamento in json['paymentlines']:
            pagamentos.append(self.__prepare_payment(pagamento))

        kwargs = {}
        if json['client']:
            # TODO: Verificar se tamanho == 14: cnpj
            kwargs['destinatario'] = Destinatario(CPF=json['client'])
        emitente = Emitente(
                CNPJ=punctuation_rm(json['company']['cnpj']),
                IE=punctuation_rm(json['company']['ie']),
                IM=punctuation_rm(json['company']['im']),
                #cRegTribISSQN=punctuation_rm(json['company']['cRegTribISSQN']),
                indRatISSQN='N')
        emitente.validar()

        # TOdo Fazer informações em configurações de POS
        informacoes_adicionais = []
        text_adc = json['info_sat']
        if '@federal' in json['info_sat']:
            fed = str('%.2f' % federal)
            text_adc = json['info_sat'].replace('@federal',fed)
        if '@estadual' in json['info_sat']:
            est = str('%.2f' % estadual)
            text_adc = text_adc.replace('@estadual',est)
        if '@municipal' in json['info_sat']:
            mun = str('%.2f' % municipal)
            text_adc = text_adc.replace('@municipal',mun)
        if '@vendedor' in json['info_sat']:
            text_adc = text_adc.replace('@vendedor',vendedor)
        if '@ganhos' in json['info_sat']:
            if json['venda'].partner_id:
                text_adc = text_adc.replace('@ganhos',str('%.2f' % json['venda'].points_won))
            else:
                text_adc = text_adc.replace('@ganhos','0')
        if '@gastos' in json['info_sat']:
            if json['venda'].partner_id:
                text_adc = text_adc.replace('@gastos',str('%.2f' % json['venda'].points_spend))
            else:
                text_adc = text_adc.replace('@gastos',"0")
        if '@restante' in json['info_sat']:
            if json['venda'].partner_id:
                text_adc = text_adc.replace('@restante',str('%.2f' % json['venda'].loyalty_points))
            else:
                text_adc = text_adc.replace('@restante',"0")

        informacoes_adicionais = InformacoesAdicionais(infCpl=text_adc)

        return CFeVenda(
                CNPJ=json['company']['cnpj_software_house'],
                signAC=self.assinatura,
                numeroCaixa=2,
                emitente=emitente,
                detalhamentos=detalhamentos,
                pagamentos=pagamentos,
                informacoes_adicionais=informacoes_adicionais,
                vCFeLei12741=total_taxes,
               # descontos_acrescimos_subtotal=descontos_acrescimos_subtotal,
                **kwargs
            )

    def _send_cfe(self, json, venda):
        resposta = self.device.enviar_dados_venda(
            self.__prepare_send_cfe(json))
        self.env['pos.order.log'].sudo().create({'pos_order_id':venda.id,'log':'Enviado com sucesso - %s / Sessao - %s' % (resposta.chaveConsulta,resposta.numeroSessao)})
        attachment = {
            'name': resposta.chaveConsulta,
            'datas': base64.b64encode(resposta.arquivoCFeSAT),
            'datas_fname': '%s.xml' % resposta.chaveConsulta,
            'res_model': 'pos.order',
            'res_id': venda.id,
        }
        self.env['ir.attachment'].create(attachment)
        venda.sudo().write({'chave_cfe': resposta.chaveConsulta,
                            'num_sessao_cfe':resposta.numeroSessao,
                            'xml_cfe_retorn':resposta.arquivoCFeSAT})
        self._print_extrato_venda(resposta.arquivoCFeSAT,resposta.chaveConsulta)
        return {
            'xml': resposta.arquivoCFeSAT,
            'numSessao': resposta.numeroSessao,
            'chave_cfe': resposta.chaveConsulta,
        }

    def __prepare_cancel_cfe(self, chCanc, cnpj, doc_destinatario):
        kwargs = {}
        if doc_destinatario:
            kwargs['destinatario'] = Destinatario(CPF=doc_destinatario)
        return CFeCancelamento(
            chCanc=chCanc,
            CNPJ=cnpj,
            signAC=self.assinatura,
            numeroCaixa=2,
            **kwargs
        )

    def _cancel_cfe(self, order, venda):
        resposta = self.device.cancelar_ultima_venda(
            order['chaveConsulta'],
            self.__prepare_cancel_cfe(order['chaveConsulta'],
                                      order['cnpj_software_house'],
                                      order['doc_destinatario'])
        )
        self._print_extrato_cancelamento(
            order['chaveConsulta'], resposta.arquivoCFeBase64, venda)
        return {
            'order_id': order['order_id'],
            'xml': resposta.arquivoCFeBase64,
            'numSessao': resposta.numeroSessao,
            'chave_cfe': resposta.chaveConsulta,
        }

    def action_call_sat(self, task, json=False):

        _logger.info('SAT: Task {0}'.format(task))

        try:
            with self.satlock:
                if task == 'connect':
                    pass
                elif task == 'get_device':
                    return self._get_device()
                elif task == 'reprint':
                    return self._reprint_cfe(json)
                elif task == 'send':
                    return self._send_cfe(json)
                elif task == 'cancel':
                    return self._cancel_cfe(json)
        except ErroRespostaSATInvalida as ex:
            _logger.error('SAT Error: {0}'.format(ex))
            return {'excessao': ex}
        except ExcecaoRespostaSAT as ex:
            _logger.error('SAT Error: {0}'.format(ex))
            return {'excessao': ex}
        except Exception as ex:
            _logger.error('SAT Error: {0}'.format(ex))
            return {'excessao': ex}

    def _init_printer(self):


        if self.impressora == 'epson-tm-t20':
            _logger.info(u'SAT Impressao: Epson TM-T20')
            from escpos.impl.epson import TMT20 as Printer
        elif self.impressora == 'bematech-mp4200th':
            _logger.info(u'SAT Impressao: Bematech MP4200TH')
            from escpos.impl.bematech import MP4200TH as Printer
        elif self.impressora == 'daruma-dr700':
            _logger.info(u'SAT Impressao: Daruma Dr700')
            from escpos.impl.daruma import DR700 as Printer
        elif self.impressora == 'elgin-i9':
            _logger.info(u'SAT Impressao: Elgin I9')
            from escpos.impl.elgin import ElginI9 as Printer
        else:
            self.printer = False

        if self.print_connection == 'network':
            conn = NetworkConnection.create(self.printer_params)
        else:
            conn = SerialSettings.as_from(
                self.printer_params).get_connection()
        self.conn = conn
        printer = Printer(conn)
        printer.init()
        return printer


    def _print_extrato_venda(self, xml, chave):
        #self.printer = self._init_printer()
        if not self.printer:
            return False
        nchave = '%s' % chave
        w_file = open(str('/tmp'+'/'+nchave+'.xml'), 'w')
        w_file.write(base64.b64decode(xml))
        w_file.close()
        extrato = ExtratoCFeVenda(
            #'/home/jefferson/teste2.xml',
            str('/tmp'+'/'+nchave+'.xml'),
            self.printer
            )
        try:
            extrato.imprimir()
        except:
            self.conn._assert_readable()
            extrato.imprimir()
        return True

    def _print_extrato_cancelamento(self, xml_venda, xml_cancelamento, venda):
        #self.printer = self._init_printer()
        if not self.printer:
            return False
        if not venda.chave_cfe_can:
	    chav_can = 'cancelamento'
	else:
	    chav_can = venda.chave_cfe_can
        nchave = '%s' % chav_can
        w_file = open(str('/tmp'+'/'+'can-'+nchave+'.xml'), 'w')
        w_file.write(base64.b64decode(xml_cancelamento))
        w_file.close()
        nchave = '%s' % xml_venda
        w_file = open(str('/tmp' + '/' + nchave + '.xml'), 'w')
        w_file.write(base64.b64decode(venda.xml_cfe_retorn))
        w_file.close()
        extrato = ExtratoCFeCancelamento(
            #StringIO.StringIO(base64.b64decode(xml_venda)),
            str('/tmp'+'/'+xml_venda+'.xml'),
            #StringIO.StringIO(base64.b64decode(xml_cancelamento)),
            str('/tmp'+'/'+'can-'+chav_can+'.xml'),
            self.printer
            )
        try:
            extrato.imprimir()
        except:
            self.conn._assert_readable()
            extrato.imprimir()
        return True

    def _print_extrato_reprint(self, xml, chave, venda):
        # try:
        #     self.printer = self._init_printer()
        # except Exception, e:
        #     _logger.info(e)
        if not self.printer:
            return False
        nchave = '%s' % chave
        w_file = open(str('/tmp'+'/reprint-'+nchave+'.xml'), 'w')
        w_file.write(base64.b64decode(venda.xml_cfe_retorn))
        w_file.close()
        extrato = ExtratoCFeVenda(
            #'/home/jefferson/teste2.xml',
            str('/tmp'+'/reprint-'+nchave+'.xml'),
            self.printer
        )
        try:
            extrato.imprimir()
        except:
            self.conn._assert_readable()
            #self._init_printer()
            extrato.imprimir()
        return True

    def _reprint_cfe(self, json, venda):
        if json['canceled_order']:
            return self._print_extrato_cancelamento(
                json['xml_cfe_venda'], json['xml_cfe_cacelada'], venda)
        else:
            return self._print_extrato_reprint( json['xml_cfe_venda'], json['chave'], venda)

    def run(self):
        self.device = None
        while True:
            if self.device:
                self.status_sat()
                time.sleep(40)
            else:
                self.device = self.action_call_sat('get_device')
                if not self.device:
                    time.sleep(40)

#     def enviar_cfe_sat(self, json):
#         return hw_proxy.drivers['satcfe'].action_call_sat('send', json)
#
# class SatDriver(hw_proxy.Proxy):
#
#     # TODO: Temos um problema quando o sat é iniciado depois do POS
#     # @http.route('/hw_proxy/status_json', type='json', auth='none', cors='*')
#     # def status_json(self):
#     #     if not hw_proxy.drivers['satcfe'].device:
#     #         hw_proxy.drivers['satcfe'].get_device()
#     #     return self.get_status()
#
#     @http.route('/hw_proxy/init/', type='json', auth='none', cors='*')
#     def init(self, json):
#         hw_proxy.drivers['satcfe'] = Sat(**json)
#         return True
#
#     @http.route('/hw_proxy/enviar_cfe_sat/', type='json', auth='none', cors='*')
#     def enviar_cfe_sat(self, json):
#         return hw_proxy.drivers['satcfe'].action_call_sat('send', json)
#
#     @http.route('/hw_proxy/cancelar_cfe/', type='json', auth='none', cors='*')
#     def cancelar_cfe(self, json):
#         return hw_proxy.drivers['satcfe'].action_call_sat('cancel', json)
#
#     @http.route('/hw_proxy/reprint_cfe/', type='json', auth='none', cors='*')
#     def reprint_cfe(self, json):
#         return hw_proxy.drivers['satcfe'].action_call_sat('reprint', json)
