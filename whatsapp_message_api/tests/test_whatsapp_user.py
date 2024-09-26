from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError

class TestWhatsappUserWithRealAPI(TransactionCase):

    def setUp(self):
        super(TestWhatsappUserWithRealAPI, self).setUp()
        # Puedes preparar algún dato específico aquí si es necesario
        self.expected_serialized = '593979078629@c.us'

    def test_initial_load_with_real_api(self):
        WhatsappUser = self.env['whatsapp_message_api.whatsapp_user']

        # Realiza la carga inicial de datos desde la API real
        WhatsappUser.initial_load()

        # Verifica que el usuario se haya creado o actualizado correctamente
        user = WhatsappUser.search([('serialized', '=', self.expected_serialized)])
        self.assertTrue(user, "El usuario no se creó o no se encontró.")
        self.assertIsNotNone(user.phone_number, "El número de teléfono no debería estar vacío.")
        self.assertIsNotNone(user.display_name, "El nombre para mostrar no debería estar vacío.")
        self.assertEqual(user.serialized, self.expected_serialized, "El campo 'serialized' no coincide.")

        # Mensaje de éxito y detalles del usuario
        if user:
            print(f"Prueba exitosa: El usuario se creó correctamente.\n"
                  f"ID: {user.id}, "
                  f"Phone Number: {user.phone_number}, "
                  f"Display Name: {user.display_name}, "
                  f"Serialized: {user.serialized}")
