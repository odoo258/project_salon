<?php
header('Access-Control-Allow-Origin: *','');
header('Content-Type: charset=utf-8');
?>
    <input type="hidden" id="user_id" title="user_id">
    <input type="hidden" id="task_id" title="task_id">

    <div class="bs-callout bs-callout-info">
        <div id="alert-info" class="alert alert-info col-md-12" style="display: none">
            <a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>
            <strong>Informação!</strong> <span class="alert-info-msg">msg</span>
        </div>

        <div id="alert-danger" class="alert alert-danger col-md-12" style="display: none">
            <a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>
            <strong>Erro!</strong> <span class="alert-danger-msg">msg</span>
        </div>
    </div>

    <div class="panel panel-default">
        <div class="panel-heading">
            <strong>Testar Dispositivo</strong>
        </div>
        <div class="panel-body">
            <ul class="list-unstyled">
                <li>
                    <strong data-oe-model="product.attribute" data-oe-id="2" data-oe-field="name" data-oe-type="char" data-oe-expression="variant_id.attribute_id.name" data-oe-translate="1">Número de Série</strong>
                    <input type="text" name="serial_number" id="serial_number"> 
                    <button type="button" name="pesquisar" id="pesquisar">Pesquisar</button>
                </li>
                <li>&nbsp;</li>

                <li id="device_buttons" style="display: none">
                    <span id="car-test" class="btn btn-default">
                        Car&nbsp;<span class="status"></span>&nbsp;<i class="fa fa-car" aria-hidden="true"></i>
                    </span>
                    <span id="gps-test" class="btn btn-default">
                        GPS&nbsp;<span class="status"></span>&nbsp;<i class="fa fa-location-arrow" aria-hidden="true"></i>
                    </span>
                    <span id="gps-valid" class="btn btn-default">
                        Position&nbsp;<span class="status"></span>&nbsp;<i class="fa fa-map-marker" aria-hidden="true"></i>
                    </span>
                </li>
            </ul>
        </div>
        <div class="panel-footer">
            <button type="button" id="fechar" class="oe_link" data-dismiss="modal">Fechar</button>
            <button type="button" id="salvar" class="oe_highlight">Salvar ></button>
        </div>
    </div>

<script type="text/javascript" src="/vehicle_service/static/src/js/device-control.js"/>
