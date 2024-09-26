from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class WhatsappGroupMember(models.Model):
    _name = 'whatsapp_message_api.whatsapp_group_member'
    _description = 'Whatsapp Group Member'

    serialized = fields.Char('Serialized')
    phone_number = fields.Char('Phone Number')
    group_id = fields.Many2one('whatsapp_message_api.whatsapp_group', string='Group', ondelete='cascade')
    
    _sql_constraints = [
        ('unique_group_user', 'unique(group_id, phone_number)', 'A user can only be a member of the same group once.')
    ]

    @api.model
    def create_or_update_members(self, group_id, participants):
        """Crea o actualiza los miembros del grupo en la base de datos"""
        try:
            if not isinstance(participants, list):
                raise UserError("Participants data is not in expected format.")
        
            # Primero, actualizamos o creamos los miembros, no eliminamos todos
            existing_members = self.search([('group_id', '=', group_id)])
            existing_serialized = set(existing_members.mapped('serialized'))
            new_serialized = set()
            
            for member_data in participants:
                serialized = member_data['id'].get('_serialized')
                phone_number = member_data['id'].get('user')
                if not serialized or not phone_number:
                    continue

                new_serialized.add(serialized)
                if serialized in existing_serialized:
                    existing_members.filtered(lambda r: r.serialized == serialized).write({
                        'phone_number': phone_number,
                        'group_id': group_id,
                    })
                else:
                    self.create({
                        'serialized': serialized,
                        'phone_number': phone_number,
                        'group_id': group_id,
                    })
            
            # Eliminar miembros que ya no están en el grupo
            to_delete = existing_members.filtered(lambda r: r.serialized not in new_serialized)
            to_delete.unlink()
            
        except Exception as e:
            _logger.error(f"Error al crear o actualizar los miembros del grupo: {e}")
            raise UserError(f"Error al crear o actualizar los miembros del grupo: {e}")
