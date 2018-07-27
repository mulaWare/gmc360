from odoo import api, fields, models

import urllib.parse
import requests
import datetime

class ResPartner(models.Model):
    _inherit = "res.partner"

    name_short = fields.Char(string="Nombre Corto", required=False)
    casfim = fields.Integer(string="CASFIM", required=False)
    figura = fields.Selection([('00','No disponible'),
                               ('01','SOFOM ENR'),
                               ('02','SOFOM ER'),
                               ('03','SOFIPO'),
                               ('04','Almacen Gral de Depósito'),
                               ('05','Asociación'),
                               ('06','Banco'),
                               ('07','Centro Cambiario'),
                               ('08','Federación de SOCAP'),
                               ('09','Persona Física'),
                               ('10','SA de CV'),
                               ('11','SAPI'),
                               ('12','SC'),
                               ('13','S de RL de CV'),
                               ('14','SOCAP'),
                               ('15','Unión de Crédito'),
                              ],
                              string="Figura", required=False, help="Tipo de figura")
    zona = fields.Selection([('00','No disponible'),
                               ('01','Norte'),
                               ('02','Sur'),
                               ('03','Este'),
                               ('04','Oeste'),
                               ('05','Noreste'),
                               ('06','Noroeste'),
                               ('07','Sureste'),
                               ('08','Suroeste'),
                               ('09','Centro'),
                               ('10','Centro-Norte'),
                               ('11','Centro-Sur'),
                              ],
                              string="Zona", required=False, help="Zona Geográfica")
