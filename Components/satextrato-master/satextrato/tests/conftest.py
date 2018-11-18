# -*- coding: utf-8 -*-
#
# satextrato/tests/conftest.py
#
# Copyright 2015 Base4 Sistemas Ltda ME
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import importlib
import sys

import pytest


def pytest_addoption(parser):

    parser.addoption('--escpos-impl', action='store',
            default='escpos.impl.epson.GenericESCPOS',
            help='implementacao ESC/POS a ser instanciada')

    parser.addoption('--escpos-if', action='store', default='serial',
            help='interface ESC/POS a ser utilizada (serial, network)')

    # serial (RS232), configurações de porta
    default_port = 'COM1' if 'win' in sys.platform else '/dev/ttyS0'

    parser.addoption('--serial-port', action='store', default=default_port,
            help='porta serial, nome da porta')

    parser.addoption('--serial-baudrate', action='store', default='9600',
            help='porta serial, velocidade de transmissao')

    parser.addoption('--serial-databits', action='store', default='8',
            help='porta serial, bits de dados')

    parser.addoption('--serial-stopbits', action='store', default='1',
            help='porta serial, bits de parada')

    parser.addoption('--serial-parity', action='store', default='N',
            help='porta serial, paridade')

    parser.addoption('--serial-protocol', action='store', default='RTSCTS',
            help='porta serial, protocolo')

    # network TCP/IP
    parser.addoption('--network-host', action='store', default='10.0.0.1',
            help='endereco do host, nome de dominio ou IP')

    parser.addoption('--network-port', action='store', default='9100',
            help='numero da porta')


class InterfaceFactory(object):

    def __init__(self, request):
        self._request = request


    def get_connection(self):
        interface = self._request.config.getoption('--escpos-if')
        return getattr(self, 'create_{}_connection'.format(interface))()


    def create_serial_connection(self):
        from escpos.serial import SerialConnection
        options = [
                self._request.config.getoption('--serial-port'),
                self._request.config.getoption('--serial-baudrate'),
                self._request.config.getoption('--serial-databits'),
                self._request.config.getoption('--serial-stopbits'),
                self._request.config.getoption('--serial-parity'),
                self._request.config.getoption('--serial-protocol'),]
        conn = SerialConnection.create(':'.join(options))
        return conn


    def create_network_connection(self):
        from escpos.network import NetworkConnection
        options = [
                self._request.config.getoption('--network-host'),
                self._request.config.getoption('--network-port'),]
        conn = NetworkConnection.create(':'.join(options))
        return conn


@pytest.fixture(scope='module')
def escpos_interface(request):
    factory = InterfaceFactory(request)
    return factory.get_connection()


@pytest.fixture(scope='module')
def escpos_impl(request):
    names = request.config.getoption('--escpos-impl').split('.')
    _module = importlib.import_module('.'.join(names[:-1]))
    return getattr(_module, names[-1])


@pytest.fixture(scope='module')
def xml_venda():
    return XML_VENDA


@pytest.fixture(scope='module')
def xml_cancelamento():
    return XML_CANCELAMENTO


XML_VENDA = u"""<?xml version="1.0"?>
<CFe>
  <infCFe Id="CFe35150808723218000186599000040190000241114257"
        versao="0.06" versaoDadosEnt="0.06" versaoSB="010000">
    <ide>
      <cUF>35</cUF>
      <cNF>111425</cNF>
      <mod>59</mod>
      <nserieSAT>900004019</nserieSAT>
      <nCFe>000024</nCFe>
      <dEmi>20150806</dEmi>
      <hEmi>195048</hEmi>
      <cDV>7</cDV>
      <tpAmb>2</tpAmb>
      <CNPJ>16716114000172</CNPJ>
      <signAC>SGR-SAT SISTEMA DE GESTAO E RETAGUARDA DO SAT</signAC>
      <assinaturaQRCODE>dZXFmGq2V0W5C2muk2E6U1CI8mMzcThNKZoAVhknRPR5BvQtMFAo8cUQOJZA5DFil5fkb6XqhZNszms6/KvZTh+NJ1ZvdYnRMBxJ19WRheMNyMxtzZz72b1IbVNGPedU46lWuXDd83kb+O4GOU6l0DSTQE1Nv2jNSLCQQtYY2LMN7yqCL3IRYSaA2UuDmezk/szP02+nB3sccKECV05QCbVc42qxzsgD5xN8IH202m5np51Cocg+rDm1LdytrJpBbetIyUUHaeponC1bnDBMKn/AvvkF4mgD+3rseHqd7S0oOdDqFOnQ8J+ZvAG1WA+7Q1mdnXyWjgsbbJsOxXefAA==</assinaturaQRCODE>
      <numeroCaixa>123</numeroCaixa>
    </ide>
    <emit>
      <CNPJ>08723218000186</CNPJ>
      <xNome>TANCA INFORMATICA EIRELI</xNome>
      <xFant>TANCA</xFant>
      <enderEmit>
        <xLgr>RUA ENGENHEIRO JORGE OLIVA</xLgr>
        <nro>73</nro>
        <xBairro>VILA MASCOTE</xBairro>
        <xMun>SAO PAULO</xMun>
        <CEP>04362060</CEP>
      </enderEmit>
      <IE>149626224113</IE>
      <IM>123123</IM>
      <cRegTrib>3</cRegTrib>
      <indRatISSQN>N</indRatISSQN>
    </emit>
    <dest/>
    <det nItem="1">
      <prod>
        <cProd>0001</cProd>
        <cEAN>0012345678905</cEAN>
        <xProd>Trib ICMS Integral Aliquota 10.00% - PIS e COFINS cod 08 sem incidencia</xProd>
        <NCM>47061000</NCM>
        <CFOP>5001</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>100.00</vUnCom>
        <vProd>100.00</vProd>
        <indRegra>A</indRegra>
        <vItem>100.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <vItem12741>1.00</vItem12741>
        <ICMS>
          <ICMS00>
            <Orig>0</Orig>
            <CST>00</CST>
            <pICMS>10.00</pICMS>
            <vICMS>10.00</vICMS>
          </ICMS00>
        </ICMS>
        <PIS>
          <PISNT>
            <CST>08</CST>
          </PISNT>
        </PIS>
        <COFINS>
          <COFINSNT>
            <CST>08</CST>
          </COFINSNT>
        </COFINS>
      </imposto>
    </det>
    <det nItem="2">
      <prod>
        <cProd>0002</cProd>
        <xProd>Trib ICMS red BC Aliquota 20% - PIS e COFINS cod 08 sem incidencia</xProd>
        <NCM>48021000</NCM>
        <CFOP>5002</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>20.00</vUnCom>
        <vProd>20.00</vProd>
        <indRegra>A</indRegra>
        <vItem>20.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <vItem12741>2.00</vItem12741>
        <ICMS>
          <ICMS00>
            <Orig>0</Orig>
            <CST>20</CST>
            <pICMS>20.00</pICMS>
            <vICMS>4.00</vICMS>
          </ICMS00>
        </ICMS>
        <PIS>
          <PISNT>
            <CST>08</CST>
          </PISNT>
        </PIS>
        <COFINS>
          <COFINSNT>
            <CST>08</CST>
          </COFINSNT>
        </COFINS>
      </imposto>
    </det>
    <det nItem="3">
      <prod>
        <cProd>0003</cProd>
        <xProd>Trib ICMS Isento - PIS e COFINS cod 08 sem incidencia</xProd>
        <NCM>54031000</NCM>
        <CFOP>5003</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>30.00</vUnCom>
        <vProd>30.00</vProd>
        <indRegra>A</indRegra>
        <vItem>30.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <vItem12741>0.00</vItem12741>
        <ICMS>
          <ICMS40>
            <Orig>0</Orig>
            <CST>40</CST>
          </ICMS40>
        </ICMS>
        <PIS>
          <PISNT>
            <CST>08</CST>
          </PISNT>
        </PIS>
        <COFINS>
          <COFINSNT>
            <CST>08</CST>
          </COFINSNT>
        </COFINS>
      </imposto>
    </det>
    <det nItem="4">
      <prod>
        <cProd>0004</cProd>
        <xProd>Trib ICMS N&#xE3;o Tributado - PIS e COFINS cod 08 sem incidencia</xProd>
        <NCM>55031100</NCM>
        <CFOP>5004</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>40.00</vUnCom>
        <vProd>40.00</vProd>
        <indRegra>A</indRegra>
        <vItem>40.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <vItem12741>0.00</vItem12741>
        <ICMS>
          <ICMS40>
            <Orig>0</Orig>
            <CST>41</CST>
          </ICMS40>
        </ICMS>
        <PIS>
          <PISNT>
            <CST>08</CST>
          </PISNT>
        </PIS>
        <COFINS>
          <COFINSNT>
            <CST>08</CST>
          </COFINSNT>
        </COFINS>
      </imposto>
    </det>
    <det nItem="5">
      <prod>
        <cProd>0005</cProd>
        <xProd>Trib ICMS Susp - PIS e COFINS cod 08 sem incidencia</xProd>
        <NCM>56031130</NCM>
        <CFOP>5005</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>50.00</vUnCom>
        <vProd>50.00</vProd>
        <indRegra>A</indRegra>
        <vItem>50.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <vItem12741>5.00</vItem12741>
        <ICMS>
          <ICMS40>
            <Orig>0</Orig>
            <CST>50</CST>
          </ICMS40>
        </ICMS>
        <PIS>
          <PISNT>
            <CST>08</CST>
          </PISNT>
        </PIS>
        <COFINS>
          <COFINSNT>
            <CST>08</CST>
          </COFINSNT>
        </COFINS>
      </imposto>
    </det>
    <det nItem="6">
      <prod>
        <cProd>0006</cProd>
        <xProd>Trib ICMS Com Ant por ST - PIS e COFINS cod 08 sem incidencia</xProd>
        <NCM>57029100</NCM>
        <CFOP>5006</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>60.00</vUnCom>
        <vProd>60.00</vProd>
        <indRegra>A</indRegra>
        <vItem>60.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <vItem12741>6.00</vItem12741>
        <ICMS>
          <ICMS40>
            <Orig>0</Orig>
            <CST>60</CST>
          </ICMS40>
        </ICMS>
        <PIS>
          <PISNT>
            <CST>08</CST>
          </PISNT>
        </PIS>
        <COFINS>
          <COFINSNT>
            <CST>08</CST>
          </COFINSNT>
        </COFINS>
      </imposto>
    </det>
    <det nItem="7">
      <prod>
        <cProd>0007</cProd>
        <xProd>Trib ICMS pelo Simples - PIS e COFINS cod 08 sem incidencia</xProd>
        <NCM>58042990</NCM>
        <CFOP>5007</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>70.00</vUnCom>
        <vProd>70.00</vProd>
        <indRegra>A</indRegra>
        <vItem>70.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <vItem12741>7.00</vItem12741>
        <ICMS>
          <ICMSSN102>
            <Orig>0</Orig>
            <CSOSN>500</CSOSN>
          </ICMSSN102>
        </ICMS>
        <PIS>
          <PISNT>
            <CST>08</CST>
          </PISNT>
        </PIS>
        <COFINS>
          <COFINSNT>
            <CST>08</CST>
          </COFINSNT>
        </COFINS>
      </imposto>
    </det>
    <det nItem="8">
      <prod>
        <cProd>0011</cProd>
        <xProd>Trib Integral Aliquota 10.00% - PIS e COFINS cod 01 aliquota 0.0150</xProd>
        <NCM>58081000</NCM>
        <CFOP>5011</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>100.00</vUnCom>
        <vProd>100.00</vProd>
        <indRegra>A</indRegra>
        <vItem>100.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <ICMS>
          <ICMS00>
            <Orig>0</Orig>
            <CST>00</CST>
            <pICMS>10.00</pICMS>
            <vICMS>10.00</vICMS>
          </ICMS00>
        </ICMS>
        <PIS>
          <PISAliq>
            <CST>01</CST>
            <vBC>100.00</vBC>
            <pPIS>0.0150</pPIS>
            <vPIS>1.50</vPIS>
          </PISAliq>
        </PIS>
        <COFINS>
          <COFINSAliq>
            <CST>01</CST>
            <vBC>100.00</vBC>
            <pCOFINS>0.0150</pCOFINS>
            <vCOFINS>1.50</vCOFINS>
          </COFINSAliq>
        </COFINS>
      </imposto>
    </det>
    <det nItem="9">
      <prod>
        <cProd>0012</cProd>
        <xProd>Trib red BC Aliquota 20%  - PIS e COFINS cod 01 aliquota 0.0150</xProd>
        <NCM>60019100</NCM>
        <CFOP>5012</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>20.00</vUnCom>
        <vProd>20.00</vProd>
        <indRegra>A</indRegra>
        <vItem>20.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <vItem12741>4.00</vItem12741>
        <ICMS>
          <ICMS00>
            <Orig>0</Orig>
            <CST>20</CST>
            <pICMS>20.00</pICMS>
            <vICMS>4.00</vICMS>
          </ICMS00>
        </ICMS>
        <PIS>
          <PISAliq>
            <CST>01</CST>
            <vBC>20.00</vBC>
            <pPIS>0.0150</pPIS>
            <vPIS>0.30</vPIS>
          </PISAliq>
        </PIS>
        <COFINS>
          <COFINSAliq>
            <CST>01</CST>
            <vBC>20.00</vBC>
            <pCOFINS>0.0150</pCOFINS>
            <vCOFINS>0.30</vCOFINS>
          </COFINSAliq>
        </COFINS>
      </imposto>
    </det>
    <det nItem="10">
      <prod>
        <cProd>0013</cProd>
        <xProd>Trib ICMS Isento - PIS e COFINS cod 01 aliquota 0.0150</xProd>
        <NCM>60052300</NCM>
        <CFOP>5013</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>30.00</vUnCom>
        <vProd>30.00</vProd>
        <indRegra>A</indRegra>
        <vItem>30.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <vItem12741>0.00</vItem12741>
        <ICMS>
          <ICMS40>
            <Orig>0</Orig>
            <CST>40</CST>
          </ICMS40>
        </ICMS>
        <PIS>
          <PISAliq>
            <CST>01</CST>
            <vBC>30.00</vBC>
            <pPIS>0.0150</pPIS>
            <vPIS>0.45</vPIS>
          </PISAliq>
        </PIS>
        <COFINS>
          <COFINSAliq>
            <CST>01</CST>
            <vBC>30.00</vBC>
            <pCOFINS>0.0150</pCOFINS>
            <vCOFINS>0.45</vCOFINS>
          </COFINSAliq>
        </COFINS>
      </imposto>
    </det>
    <det nItem="11">
      <prod>
        <cProd>0014</cProd>
        <xProd>Trib ICMS N&#xE3;o Tributado - PIS e COFINS cod 01 aliquota 0.0150</xProd>
        <NCM>61033300</NCM>
        <CFOP>5014</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>40.00</vUnCom>
        <vProd>40.00</vProd>
        <indRegra>A</indRegra>
        <vItem>40.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <vItem12741>0.00</vItem12741>
        <ICMS>
          <ICMS40>
            <Orig>0</Orig>
            <CST>41</CST>
          </ICMS40>
        </ICMS>
        <PIS>
          <PISAliq>
            <CST>01</CST>
            <vBC>40.00</vBC>
            <pPIS>0.0150</pPIS>
            <vPIS>0.60</vPIS>
          </PISAliq>
        </PIS>
        <COFINS>
          <COFINSAliq>
            <CST>01</CST>
            <vBC>40.00</vBC>
            <pCOFINS>0.0150</pCOFINS>
            <vCOFINS>0.60</vCOFINS>
          </COFINSAliq>
        </COFINS>
      </imposto>
    </det>
    <det nItem="12">
      <prod>
        <cProd>0015</cProd>
        <xProd>Trib ICMS Susp - PIS e COFINS cod 01 aliquota 0.0150</xProd>
        <NCM>61071200</NCM>
        <CFOP>5015</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>50.00</vUnCom>
        <vProd>50.00</vProd>
        <indRegra>A</indRegra>
        <vItem>50.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <vItem12741>5.00</vItem12741>
        <ICMS>
          <ICMS40>
            <Orig>0</Orig>
            <CST>50</CST>
          </ICMS40>
        </ICMS>
        <PIS>
          <PISAliq>
            <CST>01</CST>
            <vBC>50.00</vBC>
            <pPIS>0.0150</pPIS>
            <vPIS>0.75</vPIS>
          </PISAliq>
        </PIS>
        <COFINS>
          <COFINSAliq>
            <CST>01</CST>
            <vBC>50.00</vBC>
            <pCOFINS>0.0150</pCOFINS>
            <vCOFINS>0.75</vCOFINS>
          </COFINSAliq>
        </COFINS>
      </imposto>
    </det>
    <det nItem="13">
      <prod>
        <cProd>0016</cProd>
        <xProd>Trib ICMS Com Ant por ST - PIS e COFINS cod 01 aliquota 0.0150</xProd>
        <NCM>57029100</NCM>
        <CFOP>5016</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>60.00</vUnCom>
        <vProd>60.00</vProd>
        <indRegra>A</indRegra>
        <vItem>60.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <vItem12741>6.00</vItem12741>
        <ICMS>
          <ICMS40>
            <Orig>0</Orig>
            <CST>60</CST>
          </ICMS40>
        </ICMS>
        <PIS>
          <PISAliq>
            <CST>01</CST>
            <vBC>60.00</vBC>
            <pPIS>0.0150</pPIS>
            <vPIS>0.90</vPIS>
          </PISAliq>
        </PIS>
        <COFINS>
          <COFINSAliq>
            <CST>01</CST>
            <vBC>60.00</vBC>
            <pCOFINS>0.0150</pCOFINS>
            <vCOFINS>0.90</vCOFINS>
          </COFINSAliq>
        </COFINS>
      </imposto>
    </det>
    <det nItem="14">
      <prod>
        <cProd>0017</cProd>
        <xProd>Trib ICMS pelo Simples - PIS e COFINS cod 01 aliquota 0.0150</xProd>
        <NCM>58042990</NCM>
        <CFOP>5017</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>70.00</vUnCom>
        <vProd>70.00</vProd>
        <indRegra>A</indRegra>
        <vItem>70.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <ICMS>
          <ICMSSN102>
            <Orig>0</Orig>
            <CSOSN>500</CSOSN>
          </ICMSSN102>
        </ICMS>
        <PIS>
          <PISAliq>
            <CST>01</CST>
            <vBC>70.00</vBC>
            <pPIS>0.0150</pPIS>
            <vPIS>1.05</vPIS>
          </PISAliq>
        </PIS>
        <COFINS>
          <COFINSAliq>
            <CST>01</CST>
            <vBC>70.00</vBC>
            <pCOFINS>0.0150</pCOFINS>
            <vCOFINS>1.05</vCOFINS>
          </COFINSAliq>
        </COFINS>
      </imposto>
    </det>
    <det nItem="15">
      <prod>
        <cProd>0018</cProd>
        <xProd>Trib Integral Aliquota 10.00% - PIS e COFINS ST aliquota 0.0250</xProd>
        <NCM>58081000</NCM>
        <CFOP>5018</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>100.00</vUnCom>
        <vProd>100.00</vProd>
        <indRegra>A</indRegra>
        <vItem>100.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <ICMS>
          <ICMS00>
            <Orig>0</Orig>
            <CST>00</CST>
            <pICMS>10.00</pICMS>
            <vICMS>10.00</vICMS>
          </ICMS00>
        </ICMS>
        <PIS>
          <PISAliq>
            <CST>02</CST>
            <vBC>100.00</vBC>
            <pPIS>0.0250</pPIS>
            <vPIS>2.50</vPIS>
          </PISAliq>
        </PIS>
        <PISST>
          <vBC>100.00</vBC>
          <pPIS>0.0250</pPIS>
          <vPIS>2.50</vPIS>
        </PISST>
        <COFINS>
          <COFINSAliq>
            <CST>02</CST>
            <vBC>100.00</vBC>
            <pCOFINS>0.0250</pCOFINS>
            <vCOFINS>2.50</vCOFINS>
          </COFINSAliq>
        </COFINS>
        <COFINSST>
          <vBC>100.00</vBC>
          <pCOFINS>0.0250</pCOFINS>
          <vCOFINS>2.50</vCOFINS>
        </COFINSST>
      </imposto>
    </det>
    <det nItem="16">
      <prod>
        <cProd>0019</cProd>
        <xProd>Trib red BC Aliquota 0.20 -  PIS e COFINS ST aliquota 0.0250</xProd>
        <NCM>60019100</NCM>
        <CFOP>5019</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>20.00</vUnCom>
        <vProd>20.00</vProd>
        <indRegra>A</indRegra>
        <vItem>20.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <ICMS>
          <ICMS00>
            <Orig>0</Orig>
            <CST>20</CST>
            <pICMS>20.00</pICMS>
            <vICMS>4.00</vICMS>
          </ICMS00>
        </ICMS>
        <PIS>
          <PISAliq>
            <CST>02</CST>
            <vBC>20.00</vBC>
            <pPIS>0.0250</pPIS>
            <vPIS>0.50</vPIS>
          </PISAliq>
        </PIS>
        <PISST>
          <vBC>20.00</vBC>
          <pPIS>0.0250</pPIS>
          <vPIS>0.50</vPIS>
        </PISST>
        <COFINS>
          <COFINSAliq>
            <CST>02</CST>
            <vBC>20.00</vBC>
            <pCOFINS>0.0250</pCOFINS>
            <vCOFINS>0.50</vCOFINS>
          </COFINSAliq>
        </COFINS>
        <COFINSST>
          <vBC>20.00</vBC>
          <pCOFINS>0.0250</pCOFINS>
          <vCOFINS>0.50</vCOFINS>
        </COFINSST>
      </imposto>
    </det>
    <det nItem="17">
      <prod>
        <cProd>0020</cProd>
        <xProd>Trib ICMS Isento -  PIS e COFINS ST aliquota 0.0250</xProd>
        <NCM>60052300</NCM>
        <CFOP>5020</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>30.00</vUnCom>
        <vProd>30.00</vProd>
        <indRegra>A</indRegra>
        <vItem>30.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <ICMS>
          <ICMS40>
            <Orig>0</Orig>
            <CST>40</CST>
          </ICMS40>
        </ICMS>
        <PIS>
          <PISAliq>
            <CST>02</CST>
            <vBC>30.00</vBC>
            <pPIS>0.0250</pPIS>
            <vPIS>0.75</vPIS>
          </PISAliq>
        </PIS>
        <PISST>
          <vBC>30.00</vBC>
          <pPIS>0.0250</pPIS>
          <vPIS>0.75</vPIS>
        </PISST>
        <COFINS>
          <COFINSAliq>
            <CST>02</CST>
            <vBC>30.00</vBC>
            <pCOFINS>0.0250</pCOFINS>
            <vCOFINS>0.75</vCOFINS>
          </COFINSAliq>
        </COFINS>
        <COFINSST>
          <vBC>30.00</vBC>
          <pCOFINS>0.0250</pCOFINS>
          <vCOFINS>0.75</vCOFINS>
        </COFINSST>
      </imposto>
    </det>
    <det nItem="18">
      <prod>
        <cProd>0021</cProd>
        <xProd>Trib ICMS N&#xE3;o Tributado -  PIS e COFINS ST aliquota 0.0250</xProd>
        <NCM>61033300</NCM>
        <CFOP>5021</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>40.00</vUnCom>
        <vProd>40.00</vProd>
        <indRegra>A</indRegra>
        <vItem>40.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <ICMS>
          <ICMS40>
            <Orig>0</Orig>
            <CST>41</CST>
          </ICMS40>
        </ICMS>
        <PIS>
          <PISAliq>
            <CST>02</CST>
            <vBC>40.00</vBC>
            <pPIS>0.0250</pPIS>
            <vPIS>1.00</vPIS>
          </PISAliq>
        </PIS>
        <PISST>
          <vBC>40.00</vBC>
          <pPIS>0.0250</pPIS>
          <vPIS>1.00</vPIS>
        </PISST>
        <COFINS>
          <COFINSAliq>
            <CST>02</CST>
            <vBC>40.00</vBC>
            <pCOFINS>0.0250</pCOFINS>
            <vCOFINS>1.00</vCOFINS>
          </COFINSAliq>
        </COFINS>
        <COFINSST>
          <vBC>40.00</vBC>
          <pCOFINS>0.0250</pCOFINS>
          <vCOFINS>1.00</vCOFINS>
        </COFINSST>
      </imposto>
    </det>
    <det nItem="19">
      <prod>
        <cProd>0022</cProd>
        <xProd>Trib ICMS Susp -  PIS e COFINS ST aliquota 0.0250</xProd>
        <NCM>61071200</NCM>
        <CFOP>5022</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>50.00</vUnCom>
        <vProd>50.00</vProd>
        <indRegra>A</indRegra>
        <vItem>50.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <ICMS>
          <ICMS40>
            <Orig>0</Orig>
            <CST>50</CST>
          </ICMS40>
        </ICMS>
        <PIS>
          <PISAliq>
            <CST>02</CST>
            <vBC>50.00</vBC>
            <pPIS>0.0250</pPIS>
            <vPIS>1.25</vPIS>
          </PISAliq>
        </PIS>
        <PISST>
          <vBC>50.00</vBC>
          <pPIS>0.0250</pPIS>
          <vPIS>1.25</vPIS>
        </PISST>
        <COFINS>
          <COFINSAliq>
            <CST>02</CST>
            <vBC>50.00</vBC>
            <pCOFINS>0.0250</pCOFINS>
            <vCOFINS>1.25</vCOFINS>
          </COFINSAliq>
        </COFINS>
        <COFINSST>
          <vBC>50.00</vBC>
          <pCOFINS>0.0250</pCOFINS>
          <vCOFINS>1.25</vCOFINS>
        </COFINSST>
      </imposto>
    </det>
    <det nItem="20">
      <prod>
        <cProd>0023</cProd>
        <xProd>Trib ICMS Com Ant por ST -  PIS e COFINS ST aliquota 0.0250</xProd>
        <NCM>61124100</NCM>
        <CFOP>5023</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>60.00</vUnCom>
        <vProd>60.00</vProd>
        <indRegra>A</indRegra>
        <vItem>60.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <ICMS>
          <ICMS40>
            <Orig>0</Orig>
            <CST>60</CST>
          </ICMS40>
        </ICMS>
        <PIS>
          <PISAliq>
            <CST>02</CST>
            <vBC>60.00</vBC>
            <pPIS>0.0250</pPIS>
            <vPIS>1.50</vPIS>
          </PISAliq>
        </PIS>
        <PISST>
          <vBC>60.00</vBC>
          <pPIS>0.0250</pPIS>
          <vPIS>1.50</vPIS>
        </PISST>
        <COFINS>
          <COFINSAliq>
            <CST>02</CST>
            <vBC>60.00</vBC>
            <pCOFINS>0.0250</pCOFINS>
            <vCOFINS>1.50</vCOFINS>
          </COFINSAliq>
        </COFINS>
        <COFINSST>
          <vBC>60.00</vBC>
          <pCOFINS>0.0250</pCOFINS>
          <vCOFINS>1.50</vCOFINS>
        </COFINSST>
      </imposto>
    </det>
    <det nItem="21">
      <prod>
        <cProd>0024</cProd>
        <xProd>Trib ICMS pelo Simples -  PIS e COFINS ST aliquota 0.0250</xProd>
        <NCM>61149010</NCM>
        <CFOP>5024</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>70.00</vUnCom>
        <vProd>70.00</vProd>
        <indRegra>A</indRegra>
        <vItem>70.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <ICMS>
          <ICMSSN102>
            <Orig>0</Orig>
            <CSOSN>500</CSOSN>
          </ICMSSN102>
        </ICMS>
        <PIS>
          <PISAliq>
            <CST>02</CST>
            <vBC>70.00</vBC>
            <pPIS>0.0250</pPIS>
            <vPIS>1.75</vPIS>
          </PISAliq>
        </PIS>
        <PISST>
          <vBC>70.00</vBC>
          <pPIS>0.0250</pPIS>
          <vPIS>1.75</vPIS>
        </PISST>
        <COFINS>
          <COFINSAliq>
            <CST>02</CST>
            <vBC>70.00</vBC>
            <pCOFINS>0.0250</pCOFINS>
            <vCOFINS>1.75</vCOFINS>
          </COFINSAliq>
        </COFINS>
        <COFINSST>
          <vBC>70.00</vBC>
          <pCOFINS>0.0250</pCOFINS>
          <vCOFINS>1.75</vCOFINS>
        </COFINSST>
      </imposto>
    </det>
    <det nItem="22">
      <prod>
        <cProd>0031</cProd>
        <xProd>Trib sem ICMS -  PIS e COFINS ST aliquota 2.5 - ISSQN 3.21</xProd>
        <NCM>62061000</NCM>
        <CFOP>5025</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>100.00</vUnCom>
        <vProd>100.00</vProd>
        <indRegra>A</indRegra>
        <vItem>100.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <vItem12741>1.00</vItem12741>
        <ISSQN>
          <vDeducISSQN>0.00</vDeducISSQN>
          <vBC>100.00</vBC>
          <vAliq>003.21</vAliq>
          <vISSQN>3.21</vISSQN>
          <cMunFG>3550308</cMunFG>
          <cListServ>17.21</cListServ>
          <cServTribMun>12345678912345678912</cServTribMun>
          <cNatOp>01</cNatOp>
          <indIncFisc>2</indIncFisc>
        </ISSQN>
        <PIS>
          <PISAliq>
            <CST>02</CST>
            <vBC>100.00</vBC>
            <pPIS>0.0250</pPIS>
            <vPIS>2.50</vPIS>
          </PISAliq>
        </PIS>
        <PISST>
          <vBC>100.00</vBC>
          <pPIS>0.0250</pPIS>
          <vPIS>2.50</vPIS>
        </PISST>
        <COFINS>
          <COFINSAliq>
            <CST>02</CST>
            <vBC>100.00</vBC>
            <pCOFINS>0.0250</pCOFINS>
            <vCOFINS>2.50</vCOFINS>
          </COFINSAliq>
        </COFINS>
        <COFINSST>
          <vBC>100.00</vBC>
          <pCOFINS>0.0250</pCOFINS>
          <vCOFINS>2.50</vCOFINS>
        </COFINSST>
      </imposto>
    </det>
    <det nItem="23">
      <prod>
        <cProd>0032</cProd>
        <xProd>ISSQN sem cListServ, cServTribMun e cMunFG</xProd>
        <NCM>62061000</NCM>
        <CFOP>5025</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>100.00</vUnCom>
        <vProd>100.00</vProd>
        <indRegra>A</indRegra>
        <vItem>100.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <vItem12741>1.00</vItem12741>
        <ISSQN>
          <vDeducISSQN>0.00</vDeducISSQN>
          <vBC>100.00</vBC>
          <vAliq>003.21</vAliq>
          <vISSQN>3.21</vISSQN>
          <cNatOp>01</cNatOp>
          <indIncFisc>2</indIncFisc>
        </ISSQN>
        <PIS>
          <PISAliq>
            <CST>02</CST>
            <vBC>100.00</vBC>
            <pPIS>0.0250</pPIS>
            <vPIS>2.50</vPIS>
          </PISAliq>
        </PIS>
        <PISST>
          <vBC>100.00</vBC>
          <pPIS>0.0250</pPIS>
          <vPIS>2.50</vPIS>
        </PISST>
        <COFINS>
          <COFINSAliq>
            <CST>02</CST>
            <vBC>100.00</vBC>
            <pCOFINS>0.0250</pCOFINS>
            <vCOFINS>2.50</vCOFINS>
          </COFINSAliq>
        </COFINS>
        <COFINSST>
          <vBC>100.00</vBC>
          <pCOFINS>0.0250</pCOFINS>
          <vCOFINS>2.50</vCOFINS>
        </COFINSST>
      </imposto>
    </det>
    <det nItem="24">
      <prod>
        <cProd>0025</cProd>
        <xProd>Trib ICMS pelo Simples - PIS e COFINS pelo Simples</xProd>
        <NCM>62061000</NCM>
        <CFOP>5025</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>80.00</vUnCom>
        <vProd>80.00</vProd>
        <indRegra>T</indRegra>
        <vItem>80.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <ICMS>
          <ICMSSN102>
            <Orig>0</Orig>
            <CSOSN>500</CSOSN>
          </ICMSSN102>
        </ICMS>
        <PIS>
          <PISSN>
            <CST>49</CST>
          </PISSN>
        </PIS>
        <COFINS>
          <COFINSSN>
            <CST>49</CST>
          </COFINSSN>
        </COFINS>
      </imposto>
    </det>
    <det nItem="25">
      <prod>
        <cProd>0026</cProd>
        <xProd>PISQtidade e COFINS Qtidade</xProd>
        <NCM>61071200</NCM>
        <CFOP>5234</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>10.00</vUnCom>
        <vProd>10.00</vProd>
        <indRegra>T</indRegra>
        <vItem>10.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <ICMS>
          <ICMS00>
            <Orig>8</Orig>
            <CST>90</CST>
            <pICMS>10.00</pICMS>
            <vICMS>1.00</vICMS>
          </ICMS00>
        </ICMS>
        <PIS>
          <PISQtde>
            <CST>03</CST>
            <qBCProd>1.0000</qBCProd>
            <vAliqProd>0.0200</vAliqProd>
            <vPIS>0.02</vPIS>
          </PISQtde>
        </PIS>
        <COFINS>
          <COFINSQtde>
            <CST>03</CST>
            <qBCProd>1.0000</qBCProd>
            <vAliqProd>0.0200</vAliqProd>
            <vCOFINS>0.02</vCOFINS>
          </COFINSQtde>
        </COFINS>
      </imposto>
    </det>
    <det nItem="26">
      <prod>
        <cProd>0027</cProd>
        <xProd>ICMSOutros PISOutros COFINSOutros</xProd>
        <NCM>61033300</NCM>
        <CFOP>5687</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>10.00</vUnCom>
        <vProd>10.00</vProd>
        <indRegra>A</indRegra>
        <vItem>10.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <ICMS>
          <ICMS00>
            <Orig>7</Orig>
            <CST>90</CST>
            <pICMS>5.00</pICMS>
            <vICMS>0.50</vICMS>
          </ICMS00>
        </ICMS>
        <PIS>
          <PISOutr>
            <CST>99</CST>
            <vBC>5.00</vBC>
            <pPIS>0.0200</pPIS>
            <vPIS>0.10</vPIS>
          </PISOutr>
        </PIS>
        <COFINS>
          <COFINSOutr>
            <CST>99</CST>
            <vBC>8.00</vBC>
            <pCOFINS>0.0200</pCOFINS>
            <vCOFINS>0.16</vCOFINS>
          </COFINSOutr>
        </COFINS>
      </imposto>
    </det>
    <det nItem="27">
      <prod>
        <cProd>0028</cProd>
        <xProd>ICMS Simples IMUNE PIS e COFINS SN</xProd>
        <NCM>62093000</NCM>
        <CFOP>5375</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>15.00</vUnCom>
        <vProd>15.00</vProd>
        <indRegra>A</indRegra>
        <vItem>15.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <ICMS>
          <ICMSSN102>
            <Orig>8</Orig>
            <CSOSN>500</CSOSN>
          </ICMSSN102>
        </ICMS>
        <PIS>
          <PISSN>
            <CST>49</CST>
          </PISSN>
        </PIS>
        <COFINS>
          <COFINSSN>
            <CST>49</CST>
          </COFINSSN>
        </COFINS>
      </imposto>
    </det>
    <det nItem="28">
      <prod>
        <cProd>0029</cProd>
        <xProd>Simples Nacional Cobrado Anteriormente</xProd>
        <NCM>62113990</NCM>
        <CFOP>5924</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>20.00</vUnCom>
        <vProd>20.00</vProd>
        <indRegra>A</indRegra>
        <vItem>20.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <ICMS>
          <ICMSSN102>
            <Orig>8</Orig>
            <CSOSN>500</CSOSN>
          </ICMSSN102>
        </ICMS>
        <PIS>
          <PISSN>
            <CST>49</CST>
          </PISSN>
        </PIS>
        <COFINS>
          <COFINSSN>
            <CST>49</CST>
          </COFINSSN>
        </COFINS>
      </imposto>
    </det>
    <det nItem="29">
      <prod>
        <cProd>0030</cProd>
        <xProd>Simples Nacional Outros</xProd>
        <NCM>62149010</NCM>
        <CFOP>5298</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>23.00</vUnCom>
        <vProd>23.00</vProd>
        <indRegra>T</indRegra>
        <vItem>23.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <ICMS>
          <ICMSSN900>
            <Orig>7</Orig>
            <CSOSN>900</CSOSN>
            <pICMS>15.00</pICMS>
            <vICMS>3.45</vICMS>
          </ICMSSN900>
        </ICMS>
        <PIS>
          <PISSN>
            <CST>49</CST>
          </PISSN>
        </PIS>
        <COFINS>
          <COFINSSN>
            <CST>49</CST>
          </COFINSSN>
        </COFINS>
      </imposto>
    </det>
    <det nItem="30">
      <prod>
        <cProd>0008</cProd>
        <xProd>PISOutr Qtdade COFINSOutr Qtdade</xProd>
        <NCM>60019100</NCM>
        <CFOP>5978</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>45.00</vUnCom>
        <vProd>45.00</vProd>
        <indRegra>A</indRegra>
        <vItem>45.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <ICMS>
          <ICMS40>
            <Orig>7</Orig>
            <CST>41</CST>
          </ICMS40>
        </ICMS>
        <PIS>
          <PISOutr>
            <CST>99</CST>
            <qBCProd>1.0000</qBCProd>
            <vAliqProd>0.0100</vAliqProd>
            <vPIS>0.01</vPIS>
          </PISOutr>
        </PIS>
        <COFINS>
          <COFINSOutr>
            <CST>99</CST>
            <qBCProd>1.0000</qBCProd>
            <vAliqProd>0.0100</vAliqProd>
            <vCOFINS>0.01</vCOFINS>
          </COFINSOutr>
        </COFINS>
      </imposto>
    </det>
    <det nItem="31">
      <prod>
        <cProd>0009</cProd>
        <xProd>ICMS Imune PISST Qtidade COFINSST Qtidade</xProd>
        <NCM>82</NCM>
        <CFOP>5218</CFOP>
        <uCom>kg</uCom>
        <qCom>1.0000</qCom>
        <vUnCom>15.00</vUnCom>
        <vProd>15.00</vProd>
        <indRegra>A</indRegra>
        <vItem>15.00</vItem>
        <vRatDesc>0.00</vRatDesc>
        <vRatAcr>0.00</vRatAcr>
      </prod>
      <imposto>
        <ICMS>
          <ICMSSN102>
            <Orig>6</Orig>
            <CSOSN>500</CSOSN>
          </ICMSSN102>
        </ICMS>
        <PIS>
          <PISQtde>
            <CST>03</CST>
            <qBCProd>1.0000</qBCProd>
            <vAliqProd>0.0500</vAliqProd>
            <vPIS>0.05</vPIS>
          </PISQtde>
        </PIS>
        <PISST>
          <qBCProd>1.0000</qBCProd>
          <vAliqProd>0.0230</vAliqProd>
          <vPIS>0.02</vPIS>
        </PISST>
        <COFINS>
          <COFINSQtde>
            <CST>03</CST>
            <qBCProd>1.0000</qBCProd>
            <vAliqProd>0.0230</vAliqProd>
            <vCOFINS>0.02</vCOFINS>
          </COFINSQtde>
        </COFINS>
        <COFINSST>
          <qBCProd>1.0000</qBCProd>
          <vAliqProd>0.0230</vAliqProd>
          <vCOFINS>0.02</vCOFINS>
        </COFINSST>
      </imposto>
    </det>
    <total>
      <ICMSTot>
        <vICMS>46.95</vICMS>
        <vProd>1528.00</vProd>
        <vDesc>0.00</vDesc>
        <vPIS>19.98</vPIS>
        <vCOFINS>20.01</vCOFINS>
        <vPISST>14.27</vPISST>
        <vCOFINSST>14.27</vCOFINSST>
        <vOutro>0.00</vOutro>
      </ICMSTot>
      <vCFe>1528.00</vCFe>
      <ISSQNtot>
        <vBC>200.00</vBC>
        <vISS>6.42</vISS>
        <vPIS>5.00</vPIS>
        <vCOFINS>5.00</vCOFINS>
        <vPISST>5.00</vPISST>
        <vCOFINSST>5.00</vCOFINSST>
      </ISSQNtot>
    </total>
    <pgto>
      <MP>
        <cMP>01</cMP>
        <vMP>900.00</vMP>
      </MP>
      <MP>
        <cMP>02</cMP>
        <vMP>300.00</vMP>
      </MP>
      <MP>
        <cMP>03</cMP>
        <vMP>150.00</vMP>
        <cAdmC>004</cAdmC>
      </MP>
      <MP>
        <cMP>13</cMP>
        <vMP>150.00</vMP>
      </MP>
      <MP>
        <cMP>04</cMP>
        <vMP>150.00</vMP>
        <cAdmC>003</cAdmC>
      </MP>
      <MP>
        <cMP>04</cMP>
        <vMP>300.00</vMP>
      </MP>
      <MP>
        <cMP>05</cMP>
        <vMP>5.00</vMP>
      </MP>
      <MP>
        <cMP>10</cMP>
        <vMP>5.00</vMP>
      </MP>
      <MP>
        <cMP>11</cMP>
        <vMP>5.00</vMP>
      </MP>
      <MP>
        <cMP>12</cMP>
        <vMP>5.00</vMP>
      </MP>
      <vTroco>442.00</vTroco>
    </pgto>
    <infAdic>
      <obsFisco xCampo="xCampo1">
        <xTexto>xTexto1</xTexto>
      </obsFisco>
    </infAdic>
  </infCFe>
  <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
    <SignedInfo>
      <CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>
      <SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/>
      <Reference URI="#CFe35150808723218000186599000040190000241114257">
        <Transforms>
          <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
          <Transform Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>
        </Transforms>
        <DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>
        <DigestValue>qodsNii/z8C6KzqgRRrr25MfOBC4Xy+JXVnSsPAmd34=</DigestValue>
      </Reference>
    </SignedInfo>
    <SignatureValue>W1hmjeVB+9NHwV4rpRcjb+ah1C9iGvd/pR07ir8X273Ra111g7yLXzhaxWaxSMf8Db5KawLjEA1KGTtdteDUMhQTZnBMOXWuSvvK6i4DVdfW/ajbww0hU3oeWJw+cfDh5lKjUWccNbEA2idpO2YV10Mfddpn2rnwkFASJZxjiL1vcbCLWt76chOwvWZF84202U/4tu5OpLv5fnuJv0uL8IcGMnPJEHqI+2A8o2x5vF+Ai3iviv4yIQyvHjB/UhJBgGO5inM8Zn5gYqm+UnfRp77hOronsLCkXDFCQ8Ee606MuOO+zagrcX+503qp2QbGhkzgW0znCpQLPVTj3UBrZg==</SignatureValue>
    <KeyInfo>
      <X509Data>
        <X509Certificate>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</X509Certificate>
      </X509Data>
    </KeyInfo>
  </Signature>
</CFe>
"""

XML_CANCELAMENTO = u"""<?xml version="1.0"?>
<CFeCanc>
  <infCFe Id="CFe35150808723218000186599000040190000253347537"
        chCanc="CFe35150808723218000186599000040190000241114257" versao="0.06">
    <dEmi>20150806</dEmi>
    <hEmi>195048</hEmi>
    <ide>
      <cUF>35</cUF>
      <cNF>334753</cNF>
      <mod>59</mod>
      <nserieSAT>900004019</nserieSAT>
      <nCFe>000025</nCFe>
      <dEmi>20150806</dEmi>
      <hEmi>195130</hEmi>
      <cDV>7</cDV>
      <CNPJ>16716114000172</CNPJ>
      <signAC>SGR-SAT SISTEMA DE GESTAO E RETAGUARDA DO SAT</signAC>
      <assinaturaQRCODE>iWaAt4wjADUL5Xvx/R4yO4dHCenwfQmhgHT8uoi6eFimUgekdfANuuebfMeCIFr64bXoxP1btVIO68wVW7BCf9925atTrkAqU6huEQ8ZB17q7ZFu2ik8M13Wg6fyX/YVjrdL3Y6e72A6QuKG1fOn9A1XKR6ipSdSe/xmWaN3g+pFG+9oi7bRebxCVMe7R7zS0U6xkwUcstT5R8Cl95NPQiLeBX3OdQwnfdqe5xm3MPaeUOovpij4T2GVN9cOKrJh1SJGOclFdPWbzNnGxcmsWteN0dYrruTFjzyRQCoKob/43g86YCea3yJRaKSsdyogmWOanK6UCZ4fuq2zPXf+pQ==</assinaturaQRCODE>
      <numeroCaixa>123</numeroCaixa>
    </ide>
    <emit>
      <CNPJ>08723218000186</CNPJ>
      <xNome>TANCA INFORMATICA EIRELI</xNome>
      <enderEmit>
        <xLgr>RUA ENGENHEIRO JORGE OLIVA</xLgr>
        <xBairro>VILA MASCOTE</xBairro>
        <xMun>SAO PAULO</xMun>
        <CEP>04362060</CEP>
      </enderEmit>
      <IE>149626224113</IE>
      <IM>123123</IM>
    </emit>
    <dest/>
    <total>
      <vCFe>1528.00</vCFe>
    </total>
    <infAdic>
      <obsFisco xCampo="xCampo1">
        <xTexto>xTexto1</xTexto>
      </obsFisco>
    </infAdic>
  </infCFe>
  <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
    <SignedInfo>
      <CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>
      <SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/>
      <Reference URI="#CFe35150808723218000186599000040190000253347537">
        <Transforms>
          <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
          <Transform Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>
        </Transforms>
        <DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>
        <DigestValue>y79pT2P3JTWQoa1mv59qFuAVjesL8p0oByW9rUnE+oM=</DigestValue>
      </Reference>
    </SignedInfo>
    <SignatureValue>l5qSLXQlSXOMfgjaFcL+T28pubwS16u7kYtD8Wz7xcO4rLGr4U+O9hrTDdJ0VEmLh1HfbvyFL0fnIgQPNifGxOKBG8YaE1iff1z+Hj2TnrKpy5h4FftYgWGAI2SBXfcRas87gr7oGJqYSNV9Fus4b+Pzwf2HHIp/hziyolE8X7fKxk5vQ20BnRwDRQpr1BXrWBC7ukzwrYoaQ8XZ3b65u+wYrsly7oEYDAbKevPCpTFxLRLmFRGJTsg5ekKCis6mKtpyhs2tLS9U3XLTqX/GfHIfKhU65NhYdIdGFjypuzECHHVObHfMUxJ+uOe6EEgJjhLELSgkEYWlHMfj1eomOQ==</SignatureValue>
    <KeyInfo>
      <X509Data>
        <X509Certificate>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</X509Certificate>
      </X509Data>
    </KeyInfo>
  </Signature>
</CFeCanc>
"""
