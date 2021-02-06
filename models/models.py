# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import datetime, date

class Animal(models.Model):
    _name = 'animal'
    _description = 'Tabla descritiva del ganado vacuno'

    name = fields.Char(string='Nombre del animal')
    code = fields.Char(string='Codigo animal')
    nacimiento = fields.Date(string='Fecha nacimiento')
    raza = fields.Many2one('raza', 'Raza', ondelete="restrict")
    madre_id = fields.Many2one('animal',
        'Madre',
        domain="[('sexo','=','hembra')]",
        ondelete="restrict",
        options={"'no_create_edit': True, 'no_quick_create' : True"})
    padre_id = fields.Many2one('animal',
        'Padre',
        domain="[('sexo','=','macho')]",
        ondelete="restrict")
    peso_adulto = fields.Float(string='Peso del anima adulto')
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
                              ('muerto', 'Muerto')],
        string='Estado del animal',
        default='activo',
        help='Estado del animal',
        required=True)
    contadorpartos = fields.Integer(string='contador de partos')
    observaciones = fields.Text(string='Observaciones')
    edad = fields.Char(string='Edad', compute='_compute_age')

    @api.depends('nacimiento')
    def _compute_age(self):

        for rec in self:
            rec.edad = False
            if rec.nacimiento:
                dt = str(rec.nacimiento)
                d2 = date.today()
                d1 = datetime.strptime(dt, "%Y-%m-%d").date()
                rd = relativedelta(d2, d1)
                rec.edad = "[ %s - %s - %s ]" % (str(rd.years).zfill(2), str(rd.months).zfill(2), str(rd.days).zfill(2))

    def name_get(self):
        res = []
        for field in self:
            if field.madre_id:
                res.append((field.id, '%s / %s' % (field.madre_id.name, field.name)))
            else:
                res.append((field.id, '%s' % field.name))
        return res


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
        required=True,
        options={"'no_create_edit': True, 'no_quick_create' : True"})
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
    _order = 'date desc, parto_id desc, turno'

    lote_id = fields.Many2one('lote', 'Lote Nro.', ondelete="restrict")
    date = fields.Date(related='lote_id.date', string='Fecha', store=True)
    parto_id = fields.Many2one('partos',
        'Animal/Cria',
        domain="[('estado','=','activo')]",
        ondelete="restrict",
        required=True,
        options={"'no_create_edit': True, 'no_quick_create' : True"})
    turno = fields.Selection(related='lote_id.turno', string='Turno', store=True)
    produccion = fields.Float(String='Producción')
    produccion_avg = fields.Float(compute='_produccion', store=True, group_operator="avg")

    @api.depends('produccion')
    def _produccion(self):
        for rec in self:
            rec.produccion_avg=rec.produccion

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        if args is None:
          args = []
        domain = args + [('parto_id', operator, name)]
        model_ids = self._search(domain, limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(model_ids).with_user(name_get_uid))


class Lote(models.Model):
    _name = 'lote'
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
    reportado = fields.Float(compute='_total_produccion_lote', store=True, string="Finca", help="Total que se reporta en la finca")
    recibido = fields.Float(string="Planta", help="Total que se recibe en la planta")
    diferencia = fields.Float(string='Diferencia', compute='_diferencia', store=True)
    note = fields.Text(placeholder='Espacio para describir cualquier novedad del lote')
    produccion_ids = fields.One2many("produccion", "lote_id", "Lote")
    recibo = fields.Char(String="Recibo número")

    @api.depends('produccion_ids.produccion')
    def _total_produccion_lote(self):
        for reg in self:
            reg.reportado = sum(line.produccion for line in self.produccion_ids)

    @api.depends('recibido', 'reportado')
    def _diferencia(self):
        for reg in self:
            if (reg.recibido) and (reg.recibido > 0):
                reg.diferencia = (reg.recibido or 0.0) - (reg.reportado or 0.0)
            else:
                reg.diferencia = 0.0
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('ganado.lote.sequence') or _('New')
            result = super(Lote, self).create(vals)
        return (result)
