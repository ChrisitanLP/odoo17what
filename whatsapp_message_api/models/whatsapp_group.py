from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class WhatsappGroup(models.Model):
    _name = 'whatsapp_message_api.whatsapp_group'
    _description = 'Whatsapp Group'

    serialized = fields.Char('Serialized')
    group_number = fields.Char('Group Number')
    group_name = fields.Char('Group Name')
    members = fields.One2many('whatsapp_message_api.whatsapp_group_member', 'group_id', string='Members')
    chats = fields.One2many('whatsapp_message_api.whatsapp_chat', 'group_id', string='Group Chats')

    _sql_constraints = [
        ('unique_serialized', 'unique(serialized)', 'The serialized value must be unique.')
    ]
    
    @api.model
    def create_or_update_group(self, group_data):
        """Crea o actualiza un registro de grupo en la base de datos"""
        try:
            if not isinstance(group_data, dict):
                raise UserError("Group data is not in expected format.")
            
            serialized_id = group_data['id'].get('_serialized')
            if not serialized_id or 'participants' not in group_data:
                raise UserError("Invalid group data format.")
                
            group = self.search([('serialized', '=', serialized_id)], limit=1)
            group_values = {
                'group_number': group_data['id'].get('user'),
                'group_name': group_data.get('subject'),
                'serialized': serialized_id,
            }

            if group:
                group.write(group_values)
            else:
                group = self.create(group_values)

            # Actualizar miembros del grupo
            participants = group_data.get('participants', [])
            if not isinstance(participants, list):
                raise UserError("Participants data is not in expected format.")
            
            self.env['whatsapp_message_api.whatsapp_group_member'].create_or_update_members(group.id, participants)
            
            return group.id
        
        except UserError as ue:
            _logger.error(f"UserError: {ue}")
            raise ue
        except Exception as e:
            _logger.error(f"Error al crear o actualizar el grupo: {e}")
            raise UserError(f"Error al crear o actualizar el grupo: {e}")
