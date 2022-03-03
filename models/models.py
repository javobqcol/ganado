# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import datetime, date, timedelta

_logger = logging.getLogger(__name__)

class Animal(models.Model):
    _name = 'animal'
    _description = 'Tabla descritiva del ganado vacuno'

    name = fields.Char(string='Nombre del animal', required=True)
    code = fields.Char(string='Código animal')
    nacimiento = fields.Date(string='Fecha nacimiento')
    raza_id = fields.Many2one('raza', 'Raza', ondelete='restrict')
    madre_id = fields.Many2one('animal',
                               'Madre',
                               domain="[('sexo','=','hembra')]",
                               ondelete="restrict")
    padre_id = fields.Many2one('animal',
                               'Padre',
                               domain="[('sexo','=','macho')]",
                               ondelete='restrict')
    peso_adulto = fields.Float(string='Peso del animal adulto')
    sexo = fields.Selection([('macho', 'Macho'),
                             ('hembra', 'Hembra')],
                            string='Sexo',
                            default='hembra',
                            required=True)
    estado = fields.Selection([('activo', 'Activo'),
                               ('inactivo', 'Inactivo'),
                               ('enfermo', 'Enfermo'),
                               ('preñada', 'Preñada'),
                               ('vendido', 'Vendido'),
                               ('sacrificado', 'Sacrificado'),
                               ('muerto', 'Muerto'),
                               ('externo', 'Externo')],
                              string='Estado del animal',
                              default='activo',
                              help='Estado del animal',
                              required=True)
    observaciones = fields.Text(string='Observaciones')
    edad = fields.Char(string='Edad', compute='_compute_age')
    fecha_gestacion = fields.Date(string="Fecha gestacion", compute='_days_gestation')
    dias_gestacion = fields.Integer(String='Dias Gestación', compute='_days_gestation')
    ultima_palpacion = fields.Date(string="Ultima Palpacion", compute='_days_gestation')
    multi_images = fields.One2many('multi.images', 'animal_id',
                                   'Multi Imagenes')
    compra_id = fields.Many2one('res.partner', 'Comprado a:', ondelete='restrict')
    fecha_compra = fields.Date(string="Fecha compra:")

    venta_id = fields.Many2one('res.partner', 'Vendido a', ondelete='restrict')
    fecha_venta = fields.Date(string="Fecha venta:")

    def _days_gestation(self):
        for rec in self:
            rec.dias_gestacion = False
            rec.fecha_gestacion = False
            rec.ultima_palpacion = False
            if rec.id:
                vacas = self.env['palpacion'].search([('animal_id', '=', rec.id)], order='date desc', limit=1)
                for record in vacas:
                    if record.tiempo_gest and record.tiempo_gest > 0:
                        rec.fecha_gestacion = record.date - timedelta(days=record.tiempo_gest or 0)
                        delta = date.today() - rec.fecha_gestacion
                        rec.dias_gestacion = delta.days
                    rec.ultima_palpacion = record.date
    

    @api.depends('nacimiento')
    def _compute_age(self):
        for rec in self:
            rec.edad = False
            if rec.nacimiento:
                # caric = False
                dt = str(rec.nacimiento)
                d2 = date.today()
                d1 = datetime.strptime(dt, "%Y-%m-%d").date()
                rd = relativedelta(d2, d1)
                rec.edad = "[%s-%s-%s]" % (str(rd.years).zfill(2), str(rd.months).zfill(2), str(rd.days).zfill(2))

    # def name_get(self):
    #     res = []
    #     for field in self:
    #         if field.madre_id:
    #             res.append((field.id, '%s / %s' % (field.madre_id.name, field.name)))
    #         else:
    #             res.append((field.id, '%s' % field.name))
    #     return res


class MultiImages(models.Model):
    _inherit = 'multi.images'
    _description = 'Registro fotografico de animales'
    animal_id = fields.Many2one('animal', 'Animal')


class Raza(models.Model):
    _name = 'raza'
    _description = 'Raza del ganado vacuno'

    name = fields.Char(String='Raza animal')


class Partos(models.Model):
    _name = 'partos'
    _description = 'Tabla de partos de la vaca'

    cria_id = fields.Many2one('animal',
                              'Cria',
                              ondelete="restrict",
                              required=True)
    peso_cria = fields.Float(string='peso de la cria al momento de nacer')
    peso_vaca = fields.Float(string='Peso de la vaca al momento de parir')
    estado = fields.Selection([('activo', 'Activo'),
                               ('inactivo', 'Inactivo')],
                              string='Estado',
                              default='activo',
                              required=True)
    observaciones = fields.Text(string='Observaciones')

    def name_get(self):
        res = []
        for field in self:
            res.append((field.id, '%s / %s' % (field.cria_id.madre_id.name, field.cria_id.name)))
        return res

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        if args is None:
            args = []
        domain = args + [('cria_id', operator, name)]
        model_ids = self._search(domain, limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(model_ids).with_user(name_get_uid))


class Produccion(models.Model):
    _name = 'produccion'
    _description = 'Tabla de produccion'
    _order = 'date desc, animal_id desc, turno'
    _sql_constraints = [
        ('lote_animal_turno_uniq',
         'unique(lote_id, animal_id, turno)',
         'Solo puede haber un ordeño por animal y turno para cada lote')
    ]

    lote_id = fields.Many2one('lote', 'Lote Nro.', ondelete="restrict")
    date = fields.Date(related='lote_id.date', string='Fecha', store=True)
    animal_id = fields.Many2one('animal',
                                'Animal',
                                ondelete="restrict",
                                options="{'no_create_edit': True, 'no_quick_create' : True}")

    turno = fields.Selection(related='lote_id.turno', string='Turno', store=True)
    produccion = fields.Float(String='Producción')
    produccion_avg = fields.Float(compute='_produccion', store=True, group_operator="avg")
    desecho = fields.Boolean(String="Desecho?", default=False)
    motivo = fields.Char(String="Motivo")
    active = fields.Boolean(related='lote_id.active', string='Activo', store=True)
    sequence = fields.Integer(
        string="Orden del listado"
    )

    @api.depends('produccion')
    def _produccion(self):
        for rec in self:
            rec.produccion_avg = rec.produccion

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        if args is None:
            args = []
        domain = args + [('animal_id', operator, name)]
        model_ids = self._search(domain, limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(model_ids).with_user(name_get_uid))


class Lote(models.Model):
    _name = 'lote'
    _description = 'Lote de produccion lechera'
    _order = 'name desc, date desc'

    name = fields.Char(string='Lote',
                       required=True,
                       copy=False,
                       readonly=True,
                       index=True,
                       default=lambda self: _('New'))
    date = fields.Date(string="Fecha lote", default=fields.Date.today)
    turno = fields.Selection([('am', 'Mañana'),
                              ('pm', 'Tarde')],
                             string='Turno',
                             required=True)
    reportado = fields.Float(compute='_total_produccion_lote', store=True, string="Finca",
                             help="Total que se reporta en la finca")
    recibido = fields.Float(string="Planta", help="Total que se recibe en la planta")
    diferencia = fields.Float(string='Diferencia', compute='_diferencia', store=True)
    note = fields.Text(placeholder='Espacio para describir cualquier novedad del lote')
    produccion_ids = fields.One2many("produccion", "lote_id", "Detalle")
    recibo = fields.Char(String="Recibo número")
    active = fields.Boolean(string="Lote activo?", default=True)

    @api.model
    def default_get(self, default_fields):
        res = super().default_get(default_fields)
        det = self.env['lote'].search([], limit=1)
        turno = 'am'
        fecha = det.date or fields.Date.today()
        _logger.info('********Fecha =%s, turno =%s', fecha, det.turno)

        if det.turno == 'am':
            turno ='pm'
        else:
            fecha = det.date + relativedelta(days=1)
        res.update({
            'date': fecha,
            'turno': turno,
        })
        return res

    @api.depends('produccion_ids.produccion')
    def _total_produccion_lote(self):
        for reg in self:
            reg.reportado = sum(line.produccion for line in reg.produccion_ids.search([('lote_id', '=', reg.name),
                                                                                       ('desecho', '=', False)]))

    @api.depends('recibido', 'reportado')
    def _diferencia(self):
        for reg in self:
            if reg.recibido and (reg.recibido > 0):
                reg.diferencia = (reg.recibido or 0.0) - (reg.reportado or 0.0)
            else:
                reg.diferencia = 0.0

    @api.model
    def create(self, vals):
        result = False
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('ganado.lote.sequence') or _('New')
            result = super(Lote, self).create(vals)
        return result


class Palpacion(models.Model):
    _name = 'palpacion'
    _order = 'animal_id, date desc'

    date = fields.Date(string='Fecha Palpación', required=True)
    animal_id = fields.Many2one('animal',
                                'Animal',
                                domain="[('sexo','=','hembra')]",
                                ondelete="restrict")
    tiempo_gest = fields.Integer(string='Tiempo gestacion')


class ResPartner(models.Model):
    _inherit = 'res.partner'


class Caricaturas(models.Model):
    _name = 'caricaturas'
    _description = 'Caricaturas animal'

    name = fields.Char('Etimologia', required=True)
    sexo = fields.Char('Sexo')
    age = fields.Float('Edad')
    image_128 = fields.Image("Logo", max_width=128, max_height=128)
