
        $(document).ready(function () {
            const contactsBtn = document.getElementById('contacts-btn');
            const productsBtn = document.getElementById('products-btn');
            const messagesBtn = document.getElementById('messages-btn');

            document.querySelector('header').remove();
            document.querySelector('footer').remove();

            function showTemplate(templateId) {
                $.ajax({
                    url: `/api/whatsapp/${templateId}`,
                    method: 'GET',
                    dataType: 'html',
                    success: function(data) {
                        $("#dynamic-template").html(data);
                        if (templateId === 'contacts_template') {
                            initializeSearch();
                        } else if (templateId === 'products_template') {
                            initializeProductSearch();
                        } else if (templateId === 'default_messages_template') {
                            initializeDefaultMessages();
                        }
                        handleMobileView(mediaQuery);
                    },
                    error: function() {
                        $("#dynamic-template").html('<p>Error loading template</p>');
                    }
                });
            }

            function initializeSearch() {
                const addContactBtn = $('#add-contact-btn');
                const modal_contact = $('#add-contact-modal');
                const closeContactBtnHeader = $('#header-close-modal-contact');
                const closeContactBtnFooter = $('#footer-close-modal-contact');
                const saveContactBtn = $('#save-contact-btn');

                const phoneInput = $('#contact_phone_number');
                const countryCodeSelect = $('#contact-country_code');
                const phoneError = $('#phone-error');
                const userSelect = $('#contact_user');

                addContactBtn.on('click', function () {
                    modal_contact.modal('show');
                    loadWhatsappUsers();
                });
            
                closeContactBtnHeader.on('click', function () {
                    modal_contact.modal('hide');
                });
            
                closeContactBtnFooter.on('click', function () {
                    modal_contact.modal('hide');
                });

                function loadWhatsappUsers() {
                    $.ajax({
                        url: '/api/whatsapp_users',
                        method: 'GET',
                        dataType: 'json',
                        success: function(result) {
                            if (result.status === 'success') {
                                const users = result.users;
                                userSelect.empty(); 
                                userSelect.append('<option value="">Seleccionar Usuario</option>'); 
                                users.forEach(function(user) {
                                    userSelect.append(`<option value="${user.id}">${user.name}</option>`);
                                });
                            } else {
                                console.error('Error al obtener usuarios:', result.message);
                            }
                        },
                        error: function(error) {
                            console.error('Error en la solicitud AJAX:', error);
                        }
                    });
                }

                // Función para validar el formulario de contacto
                function validateContactForm() {
                    const name = $('#contact_name').val().trim();
                    const phoneNumber = phoneInput.val().trim();
                    const countryCode = countryCodeSelect.val();
                    const userId = userSelect.val();
                    let isValid = true;

                    // Validación de campos vacíos
                    if (!name || !phoneNumber || !countryCode || !userId) {
                        Swal.fire({
                            icon: 'warning',
                            title: 'Advertencia!',
                            text: 'Todos los campos son requeridos.',
                            confirmButtonText: 'Aceptar'
                        });
                        isValid = false;
                    }

                    // Validar que el número de teléfono tenga exactamente 9 dígitos
                    if (phoneNumber.length !== 9) {
                        phoneError.show();
                        isValid = false;
                    } else {
                        phoneError.hide();
                    }

                    return isValid;
                }
            
                // Guardar el contacto al hacer clic en "Guardar"
                saveContactBtn.on('click', function () {
                    if (!validateContactForm()) {
                        return; 
                    }

                    const name = $('#contact_name').val();
                    const phoneNumber = phoneInput.val();
                    const countryCode = countryCodeSelect.val();
                    const fullNumber = countryCode + phoneNumber;
                    const userId = userSelect.val();

                    var apiUrl = '/api/contacts/save'; 
                    var csrfToken = $('meta[name="csrf-token"]').attr('content');
            
                    $.ajax({
                        url: apiUrl,
                        type: 'POST',
                        headers: {
                            'X-CSRFToken': csrfToken,
                            'Content-Type': 'application/json'
                        },
                        data: JSON.stringify({
                            clientId: userId,
                            contactNumber: fullNumber,
                            contactName: name
                        }),
                        success: function (data) {
                            if (data.result && data.result.status === 'success') {
                                Swal.fire({
                                    title: 'Éxito',
                                    text: 'Contacto añadido exitosamente.',
                                    icon: 'success',
                                    confirmButtonText: 'Aceptar'
                                }).then(() => {
                                    modal_contact.modal('hide');
                                });
                            } else if (data.result && data.result.status === 'exists') {
                                Swal.fire({
                                    title: 'Contacto Existente', 
                                    text: 'El contacto ya está guardado en el sistema.', 
                                    icon: 'info',
                                    confirmButtonText: 'Aceptar'
                                });
                            } else {
                                Swal.fire({
                                    title: 'Error!', 
                                    text: data.message || 'No se pudo guardar el contacto.', 
                                    icon: 'error',
                                    confirmButtonText: 'Aceptar'
                                });
                            }
                        },
                        error: function (xhr) {
                            let errorMessage = 'Error desconocido.';
                            if (xhr.responseJSON && xhr.responseJSON.message) {
                                errorMessage = xhr.responseJSON.message;
                            }

                            Swal.fire({
                                title: 'Error',
                                text: 'Hubo un problema al añadir el contacto: ' + errorMessage,
                                icon: 'error',
                                confirmButtonText: 'Aceptar'
                            });
                        }
                    });
                });

                const searchInput = $('#search-input');
                searchInput.on('input', function () {
                    const query = $(this).val();
                    $.ajax({
                        url: '/api/contacts/search',
                        method: 'POST',
                        data: { query: query },
                        dataType: 'json',
                        success: function(result) {
                            if (result.status === 'success') {
                                const contacts = result.contacts;
                                const contactsGrid = $('.contacts-grid');
                                contactsGrid.empty();

                                contacts.sort(function(a, b) {
                                    return a.name.localeCompare(b.name); 
                                });                                

                                contacts.forEach(function (contact) {
                                    const contactItem = `
                                        <div class="contact-item" data-contact-id="${contact.id}" data-user-id="${contact.user_id}" data-phone-number="${contact.phone_number}" data-color-contact="${contact.color}">
                                            <div class="color-line" style="background-color: ${contact.color}"></div>
                                            <div class="profile-pic"
                                                data-contact-id="${contact.id}"
                                                data-serialized="${contact.serialized}"
                                                data-user-id="${contact.user_id}"
                                                data-phone-number="${contact.phone_number}">
                                                <img src="${contact.profile_pic_url || 'https://cdn.playbuzz.com/cdn/913253cd-5a02-4bf2-83e1-18ff2cc7340f/c56157d5-5d8e-4826-89f9-361412275c35.jpg'}" alt="Profile Picture"/>
                                            </div>
                                            <div class="contact-info">
                                                <div class="contact-name">${contact.name}</div>
                                                <div class="contact-phone">${contact.phone_number}</div>
                                                <div class="contact-user">${contact.user_display_name}</div>
                                            </div>
                                            <div class="contact-plus-icon">
                                                <i class="fa fa-plus"></i>
                                            </div>
                                        </div>`;
                                    contactsGrid.append(contactItem);
                                });
                            } else {
                                console.error('Error:', result.message);
                            }
                        },
                        error: function(error) {
                            console.error('AJAX error:', error);
                        }
                    });
                });
            }

            function initializeProductSearch() {
                const searchInput = $('#search-input-products');
                searchInput.on('input', function () {
                    const query = $(this).val();
                    $.ajax({
                        url: '/api/products/search',
                        method: 'POST',
                        data: { query: query },
                        dataType: 'json',
                        success: function(result) {
                            if (result.status === 'success') {
                                const products = result.products;
                                const productsGrid = $('.products-grid');
                                productsGrid.empty();

                                products.forEach(function (product) {
                                    const productItem = `
                                        <div class="product-item" data-product-id="${product.id}">
                                            <div class="color-line"></div>
                                            <div class="product-pic">
                                                <img src="/web/image/product.template/${product.id}/image_1920" alt="Product Image"/>
                                            </div>
                                            <div class="product-info">
                                                <div class="product-name">${product.name}</div>
                                                <div class="product-price">${product.list_price} €</div>
                                            </div>
                                        </div>`;
                                    productsGrid.append(productItem);
                                });
                            } else {
                                console.error('Error:', result.message);
                            }
                        },
                        error: function(error) {
                            console.error('AJAX error:', error);
                        }
                    });
                });
            }

            function initializeDefaultMessages() {
                const addMessageBtn = $('#add-message-btn');
                const modal_message = $('#add-message-modal');
                const closeModalBtnHeader = $('#header-close-modal');
                const closeModalBtnFooter = $('#footer-close-modal');
                const saveMessageBtn = $('#save-message-btn');
                const form = $('#add-message-form');
                const messageTypeSelect = $('#message-type');
                const messageContentGroup = $('#message-content-group');
                const pdfFileGroup = $('#pdf-file-group');
                const locationGroup = $('#location-group');
                const messageContentTextarea = $('#message-content');
                const pdfFileInput = $('#pdf-file');
                const latitudeInput = $('#latitude');
                const longitudeInput = $('#longitude');
            
                addMessageBtn.on('click', function () {
                    if (navigator.appName == "Opera"){
                        modal.removeClass('fade');
                    }else {
                        modal_message.modal('show'); // Mostrar el modal usando Bootstrap
                    }
                });
            
                closeModalBtnHeader.on('click', function () {
                    modal_message.modal('hide');
                });
            
                closeModalBtnFooter.on('click', function () {
                    modal_message.modal('hide');
                });
            
                saveMessageBtn.on('click', function () {
                    const name = $('#message-name').val();
                    const type = messageTypeSelect.val();
                    const text = type === 'text' || type === 'image' || type === 'web_page' ? messageContentTextarea.val() : '';
                    const location = type === 'location' ? locationGroup.find('input').map((_, el) => $(el).val()).get().join(',') : '';
                    const location_latitude = type === 'location' ? latitudeInput.val() : '';
                    const location_longitude = type === 'location' ? longitudeInput.val() : '';
                    const pdf_file = type === 'document' || type === 'image' ? pdfFileInput.prop('files')[0] : null;
                    const file_name = pdf_file ? pdf_file.name : '';
                    const web_url = type === 'web_page' ? messageContentTextarea.val() : '';
                
                    let formData = new FormData();
                    formData.append('name', name);
                    formData.append('type', type);
                    formData.append('text', text);
                    formData.append('location', location);
                    formData.append('location_latitude', location_latitude);
                    formData.append('location_longitude', location_longitude);
                    formData.append('file_name', file_name);
                    formData.append('web_url', web_url);
                    if (pdf_file) {
                        formData.append('file', pdf_file);
                    }
                
                    $.ajax({
                        url: '/api/default_message/create',
                        method: 'POST',
                        data: formData,
                        processData: false,
                        contentType: false,
                        success: function (response) {
                            if (response.success) {
                                Swal.fire({
                                    title: 'Éxito',
                                    text: 'Mensaje creado exitosamente.',
                                    icon: 'success',
                                    confirmButtonText: 'Cerrar'
                                }).then((result) => {
                                    if (result.isConfirmed) {
                                        modal_message.modal('hide');
                                        // Actualiza la sección de mensajes
                                        $('.messages-grid').empty(); 
                                        response.messages.forEach(message => {

                                            $('.messages-grid').append(`
                                                <div class="message-item" data-message-id="${message.id}">
                                                    <div class="color-line" style="background-color: #e0ca04"></div>
                                                    <div class="send-icon" data-message-id="${message.id}">
                                                        <i class="fa fa-paper-plane"></i>
                                                    </div>
                                                    <div class="message-info">
                                                        <div class="message-name">${message.name}</div>
                                                        <div class="message-type">
                                                            ${message.type === 'text' ? message.text : ''}
                                                            ${message.type === 'location' ? `<a href="https://www.google.com/maps?q=${message.location_latitude},${message.location_longitude}" target="_blank">Ver ubicación</a>` : ''}
                                                            ${message.type === 'image' ? `<pre>${message.file_name}</pre>` : ''}
                                                            ${message.type === 'document' ? message.file_name : ''}
                                                            ${message.type === 'web_page' ? `<a href="${message.web_url}" target="_blank">Ver página</a>` : ''}
                                                        </div>
                                                    </div>
                                                    <button class="close-btn">
                                                        <i class="fa fa-times"></i>
                                                    </button>
                                                </div>
                                            `);
                                        });
                                    }
                                });
                            } else {
                                Swal.fire({
                                    title: 'Error',
                                    text: 'Hubo un problema al crear el mensaje: ' + response.message,
                                    icon: 'error',
                                    confirmButtonText: 'Cerrar'
                                });
                            }
                        },
                        error: function (xhr, status, error) {
                            let errorMessage = 'Error desconocido.';
                            if (xhr.responseJSON && xhr.responseJSON.message) {
                                errorMessage = xhr.responseJSON.message;
                            } else if (xhr.responseText) {
                                errorMessage = xhr.responseText;
                            }
                
                            Swal.fire({
                                title: 'Error',
                                text: 'Hubo un problema al crear el mensaje: ' + errorMessage,
                                icon: 'error',
                                confirmButtonText: 'Cerrar'
                            });
                        }
                    });
                });
            
                function updateFormFields() {
                    const selectedType = messageTypeSelect.val();
                    messageContentGroup.hide();
                    pdfFileGroup.hide();
                    locationGroup.hide();
                    messageContentTextarea.prop('disabled', true);
            
                    switch (selectedType) {
                        case 'text':
                        case 'web_page':
                            messageContentGroup.show();
                            messageContentTextarea.prop('disabled', false);
                            break;
                        case 'image':
                        case 'document':
                            pdfFileGroup.show();
                            break;
                        case 'location':
                            locationGroup.show();
                            break;
                        default:
                            break;
                    }
                }

                messageTypeSelect.on('change', updateFormFields);
                updateFormFields();
                
                $('.messages-grid').on('click', '.close-btn', function () {
                    // Obtener el ID del mensaje desde el data attribute
                    var messageId = $(this).closest('.message-item').data('message-id');
                
                    // Confirmar con el usuario antes de eliminar
                    Swal.fire({
                        title: '¿Estás seguro?',
                        text: "¡No podrás revertir esto!",
                        icon: 'warning',
                        showCancelButton: true,
                        confirmButtonColor: '#3085d6',
                        cancelButtonColor: '#d33',
                        confirmButtonText: 'Sí, eliminarlo'
                    }).then((result) => {
                        if (result.isConfirmed) {
                            // Realizar la solicitud AJAX para eliminar el mensaje
                            $.ajax({
                                url: '/api/default_message/delete/' + messageId,
                                method: 'DELETE',
                                dataType: 'json',
                                success: function (response) {
                                    if (response.success === 'success') {
                                        // Eliminar el elemento del DOM
                                        $('div.message-item[data-message-id="' + messageId + '"]').remove();
                                        Swal.fire(
                                            '¡Eliminado!',
                                            'El mensaje ha sido eliminado.',
                                            'success'
                                        );
                                    } else {
                                        Swal.fire(
                                            'Error',
                                            'Error al eliminar el mensaje: ' + response.message,
                                            'error'
                                        );
                                    }
                                },
                                error: function () {
                                    Swal.fire(
                                        'Error',
                                        'Error al conectar con el servidor.',
                                        'error'
                                    );
                                }
                            });
                        }
                    });
                });
                
            }

            if (contactsBtn) {
                contactsBtn.addEventListener('click', function() {
                    showTemplate('contacts_template');
                    setActiveButton('contacts-btn');
                });
            } else {
                console.warn('No se encontró el botón de contactos');
            }

            if (productsBtn) {
                productsBtn.addEventListener('click', function() {
                    showTemplate('products_template');
                    setActiveButton('products-btn');
                });
            } else {
                console.warn('No se encontró el botón de productos');
            }

            if (messagesBtn) {
                messagesBtn.addEventListener('click', function() {
                    showTemplate('default_messages_template');
                    setActiveButton('messages-btn');
                });
            } else {
                console.warn('No se encontró el botón de mensajes');
            }
            
            function setActiveButton(activeId) {
                const buttons = document.querySelectorAll('.nav-icons button');
                buttons.forEach(button => {
                    if (button.id === activeId) {
                        button.classList.add('active');
                    } else {
                        button.classList.remove('active');
                    }
                });
            }

            showTemplate('contacts_template');

            function handleMobileView(mediaQuery) {
                const container = $('.chats-and-contacts-container');
                if (mediaQuery.matches) {
                    container.addClass('mobile-view');

                    $('.chat-item').on('click', function() {
                        $('.chats-and-contacts-container').removeClass('contacts-selected products-selected default-messages-selected').addClass('chat-selected');
                    });
                    
                    // Mostrar la sección de contactos al hacer clic en el botón de contactos
                    $('#contacts-btn').on('click', function() {
                        $('.chats-and-contacts-container').removeClass('chat-selected products-selected default-messages-selected').addClass('contacts-selected');
                    });
                    
                    // Mostrar la sección de templates dinámicos al hacer clic en el botón de productos
                    $('#products-btn').on('click', function() {
                        $('.chats-and-contacts-container').removeClass('chat-selected contacts-selected default-messages-selected').addClass('products-selected');
                    });
        
                    // Mostrar la sección de templates dinámicos al hacer clic en el botón de productos
                    $('#messages-btn').on('click', function() {
                        $('.chats-and-contacts-container').removeClass('chat-selected contacts-selected products-selected').addClass('default-messages-selected');
                    });
                    
                    // Volver a la lista de chats al hacer clic en el botón de regreso
                    $('#chat-messages-btn').on('click', function() {
                        $('.chats-and-contacts-container').removeClass('chat-selected contacts-selected products-selected default-messages-selected');
                    });
        
        
                    $(document).on('click','.profile-pic', function() {
                        $('.chats-and-contacts-container').removeClass('contacts-selected products-selected default-messages-selected').addClass('chat-selected');
                    });
        
                    // Volver a la lista de chats al hacer clic en el botón de regreso
                    $(document).on('click', '#close-products-btn-section', function() {
                        $('.chats-and-contacts-container').removeClass('products-selected contacts-selected default-messages-selected').addClass('chat-selected');
                    });
                    
                    $(document).on('click', '#close-contacts-btn-section', function() {
                        $('.chats-and-contacts-container').removeClass('contacts-selected products-selected default-messages-selected').addClass('chat-selected');
                    });
                    
                    $(document).on('click', '#close-default-messages-btn-section', function() {
                        $('.chats-and-contacts-container').removeClass('default-messages-selected products-selected contacts-selected').addClass('chat-selected');
                    });
        
                    // Volver a la lista de chats al hacer clic en el botón de regreso
                    $(document).on('click', '.product-item', function() {
                        $('.chats-and-contacts-container').removeClass('products-selected contacts-selected default-messages-selected').addClass('chat-selected');
                    });
                    
                    $(document).on('click', '.send-icon', function() {
                        $('.chats-and-contacts-container').removeClass('contacts-selected products-selected default-messages-selected').addClass('chat-selected');
                    });
        
                } else {
                    container.removeClass('mobile-view');
                }
            }

            const mediaQuery = window.matchMedia('(max-width: 768px)');
            mediaQuery.addListener(handleMobileView);
            handleMobileView(mediaQuery);

            function handleTabletView(mediaQuery) {
                const container = $('.chats-and-contacts-container');
                if (mediaQuery.matches) {
                    container.addClass('tablet-view');

                    // Mostrar la sección de contactos en el área de mensajes al hacer clic en el botón de contactos
                    $('#contacts-btn').on('click', function() {
                        $('.chats-and-contacts-container').removeClass('chat-selected products-selected default-messages-selected').addClass('contacts-selected');
                    });
                    
                    // Mostrar la sección de productos en el área de mensajes al hacer clic en el botón de productos
                    $('#products-btn').on('click', function() {
                        $('.chats-and-contacts-container').removeClass('chat-selected contacts-selected default-messages-selected').addClass('products-selected');
                    });
                    
                    // Mostrar los mensajes por defecto en el área de mensajes
                    $('#messages-btn').on('click', function() {
                        $('.chats-and-contacts-container').removeClass('chat-selected contacts-selected products-selected').addClass('default-messages-selected');
                    });
                    
                    // Volver a la lista de chats al hacer clic en el botón de regreso
                    $('#chat-messages-btn').on('click', function() {
                        $('.chats-and-contacts-container').removeClass('chat-selected contacts-selected products-selected default-messages-selected');
                    });
                    
                    $(document).on('click', '#close-products-btn-section', function() {
                        $('.chats-and-contacts-container').removeClass('products-selected contacts-selected default-messages-selected').addClass('chat-selected');
                    });
                    
                    $(document).on('click', '#close-contacts-btn-section', function() {
                        $('.chats-and-contacts-container').removeClass('contacts-selected products-selected default-messages-selected').addClass('chat-selected');
                    });
                    
                    $(document).on('click', '#close-default-messages-btn-section', function() {
                        $('.chats-and-contacts-container').removeClass('default-messages-selected products-selected contacts-selected').addClass('chat-selected');
                    });
                    
                    // Aplicar la lógica para cuando se selecciona un chat o se envía un mensaje
                    $(document).on('click', '.chat-item, .send-icon, .product-item', function() {
                        $('.chats-and-contacts-container').removeClass('contacts-selected products-selected default-messages-selected').addClass('chat-selected');
                    });
                } else {
                    container.removeClass('tablet-view');
                }
            }
            
            const tabletMediaQuery = window.matchMedia('(min-width: 769px) and (max-width: 1280px)');
            tabletMediaQuery.addListener(handleTabletView);
            handleTabletView(tabletMediaQuery);
        });