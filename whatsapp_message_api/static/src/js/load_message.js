
        $(document).ready(function () {
            var selectedChatId = null;
            var selectedMessageId = null;
            var selectedSessionId = null

            // Función para obtener el ID de usuario
            function fetchSessionId() {
                var csrfToken = $('meta[name="csrf-token"]').attr('content');
                $.ajax({
                    url: '/session_id',
                    type: 'GET',
                    headers:{
                        'X-CSRFToken': csrfToken
                    },
                    success: function(data) {
                        if(data && data.status === 'success'){
                            selectedSessionId = data.session;
                            window.selectSessionUserId = selectedSessionId;
                        }
                    },
                    error: function(xhr, status, error) {
                        console.error('Ajax error: ', error);
                    }
                });
            };

            fetchSessionId();

            // Función para mostrar la sección de botón "Atender"
            function showAttendButton() {
                $('#input-disabled-container').hide();
                $('#message-input-container').hide(); 
                $('#attend-button-container').show(); 
            }

            // Función para mostrar la sección del input de mensaje
            function showMessageInput() {
                $('#input-disabled-container').hide();
                $('#attend-button-container').hide(); 
                $('#message-input-container').show();
            }
            
            function showInputDisabled() {
                $('#message-input-container').hide(); 
                $('#attend-button-container').hide(); 
                $('#input-disabled-container').show(); 
            }

            showAttendButton();

            $(document).on('click', '.chat-item', function (e) {
                e.stopPropagation();
                selectedChatId = $(this).data('chat-id'); 
                window.selectedChat = selectedChatId;
                    // Limpia el input de mensajes
                $('#message-input').val('');

                // Cierra y limpia la previsualización de archivos si está abierta
                toggleFilePreview(false);
                $('#preview-image').attr('src', '').hide();
                $('#preview-video').attr('src', '').hide();
                $('#preview-document').attr('src', '').hide();
                $('#file-message').val('');

                if (selectedChatId) {
                    $('#messages-container').show();
                    loadMessages(selectedChatId);
                } else {
                    $('#messages-container').hide(); 
                    showMessageInput(); 
                }
            });

            function toggleFilePreview(visible) {
                if (visible) {
                    $('#file-preview').addClass('visible');
                } else {
                    $('#file-preview').removeClass('visible');
                }
            }

            $(document).on('click', '.attend-button', function () {
                if (selectedChatId) {
                    $.ajax({
                        url: '/api/chat/update_status', 
                        type: 'POST',
                        headers: {
                            'X-CSRFToken': $('meta[name="csrf-token"]').attr('content'),
                            'Content-Type': 'application/json'
                        },
                        data: JSON.stringify({
                            chat_id: selectedChatId,
                            status_chat: 'atendiendo' 
                        }),
                        success: function(data) {
                            if(data.result && data.result.status === 'success'){

                                var chatItem = $('.chat-item[data-chat-id="' + selectedChatId + '"]');

                                // Si el chat no está en las secciones de chats pendientes o atendidos, lo buscas en la lista de contactos
                                if (chatItem.length === 0) {
                                    id_chat_contact = window.chat_id_contact_section;
                                    var contactItem = $('.contact-item[data-contact-id="' + window.contact_id_section + '"]');

                                     // Crear un nuevo elemento de chat basado en el contacto
                                    if (contactItem.length) {
                                        chatItem = $('<div class="chat-item" data-chat-id="' + selectedChatId + '" style="border-left: 5px solid ' + (contactItem.data('color-contact') || '#cccccc') + '">' +
                                                '<div class="profile-pic"><img src="' + contactItem.find('img').attr('src') + '" alt="Profile Picture"/></div>' +
                                                '<div class="chat-info"><div class="chat-name">' + contactItem.find('.contact-name').text() + '</div></div>' +
                                                '</div>');

                                        // Añadir los botones de cerrar chat y marcar como listo al nuevo chat
                                        chatItem.append('<div class="chat-close-icon" data-chat-id="' + id_chat_contact + '"><i class="fa fa-times-circle" aria-hidden="true"></i></div>');
                                        chatItem.append('<div class="chat-ready-icon" data-chat-id="' + id_chat_contact + '"><i class="fa fa-check-circle" aria-hidden="true"></i></div>');

                                            // Añadir el chat a la sección de "Chats Atendidos"
                                        $('.seccion-superior').append(chatItem);
                                    }
                                } else {
                                    // Mover el chat existente a la sección de "Chats Atendidos"
                                    var lastMessage = chatItem.find('.chat-info .highlighted');
                                    var unreadChat = chatItem.find('.unread-count').remove();

                                    if (lastMessage.length) lastMessage.remove();
                                    if (unreadChat.length) unreadChat.remove();

                                    chatItem.remove();
                                    $('.seccion-superior').append(chatItem);

                                    // Añadir los botones si no están presentes
                                    if (!chatItem.find('.chat-close-icon').length) {
                                        chatItem.append('<div class="chat-close-icon" data-chat-id="' + selectedChatId + '"><i class="fa fa-times-circle" aria-hidden="true"></i></div>');
                                    }
                                    if (!chatItem.find('.chat-ready-icon').length) {
                                        chatItem.append('<div class="chat-ready-icon" data-chat-id="' + selectedChatId + '"><i class="fa fa-check-circle" aria-hidden="true"></i></div>');
                                    }
                                }
                                showMessageInput();
                            }
                        },
                        error: function(xhr, status, error) {
                            console.error('Error al actualizar el estado del chat:', error);
                            Swal.fire({
                                title: 'Error!',
                                text: 'Hubo un problema al actualizar el estado del chat.',
                                icon: 'error',
                                confirmButtonText: 'Aceptar'
                            });
                        }
                    });
                } else {
                    $('#messages-container').hide(); 
                    showAttendButton();
                }
            });

            $(document).on('click', '.chat-close-icon', function () {
                selected_chat_id = $(this).data('chat-id');

                if (selected_chat_id) {
                    showAttendButton(); 

                    $.ajax({
                        url: '/api/chat/update_status', 
                        type: 'POST',
                        headers: {
                            'X-CSRFToken': $('meta[name="csrf-token"]').attr('content'),
                            'Content-Type': 'application/json'
                        },
                        data: JSON.stringify({
                            chat_id: selected_chat_id,
                            status_chat: 'pendiente' 
                        }),
                        success: function(data) {
                            if(data.result && data.result.status === 'success'){

                                // Mueve el chat a la sección de "Chats Pendientes"
                                var chatItem = $('.chat-item[data-chat-id="' + selected_chat_id + '"]');
                                var closeIcon = chatItem.find('.chat-close-icon');
                                var readyIcon = chatItem.find('.chat-ready-icon');
                                
                                // Elimina los iconos
                                if (closeIcon.length) closeIcon.remove();
                                if (readyIcon.length) readyIcon.remove();
                                
                                // Agregar elementos de unread-count y si no existen
                                if (!chatItem.find('.unread-count').length) {
                                    chatItem.append('<div class="unread-count">' + data.result.unread_count + '</div>'); // Aquí puedes ajustar el valor según sea necesario
                                }

                                if (!chatItem.find('.chat-info .highlighted').length) {
                                    var lastMessageHtml;
                                    
                                    if (data.result.last_message_body.startsWith('https://') || data.result.last_message_body.startsWith('http://')) {
                                        lastMessageHtml = '<div class="highlighted"><i class="fa fa-link message-icon" aria-hidden="true"></i><span> URL</span></div>';
                                    } else if (data.result.last_message_type === 'image') {
                                        lastMessageHtml = '<div class="highlighted"><i class="fa fa-image message-icon" aria-hidden="true"></i><span> Image</span></div>';
                                    } else if (data.result.last_message_type === 'sticker') {
                                        lastMessageHtml = '<div class="highlighted"><i class="fa fa-sticky-note message-icon" aria-hidden="true"></i><span> Sticker</span></div>';
                                    } else if (data.result.last_message_type === 'groups_v4_invite') {
                                        lastMessageHtml = '<div class="highlighted"><i class="fa fa-users message-icon" aria-hidden="true"></i><span> Invitación de Grupo</span></div>';
                                    } else if (data.result.last_message_type === 'video') {
                                        lastMessageHtml = '<div class="highlighted"><i class="fa fa-video-camera message-icon" aria-hidden="true"></i><span> Video</span></div>';
                                    } else if (data.result.last_message_type === 'vcard') {
                                        lastMessageHtml = '<div class="highlighted"><i class="fa fa-address-card message-icon" aria-hidden="true"></i><span> Contacto</span></div>';
                                    } else if (data.result.last_message_type === 'location') {
                                        lastMessageHtml = '<div class="highlighted"><i class="fa fa-map-marker message-icon" aria-hidden="true"></i><span> Ubicación</span></div>';
                                    } else if (data.result.last_message_type === 'document') {
                                        lastMessageHtml = '<div class="highlighted"><i class="fa fa-file message-icon" aria-hidden="true"></i><span> Documento</span></div>';
                                    } else if (data.result.last_message_type === 'ptt' || data.result.last_message_type === 'audio') {
                                        lastMessageHtml = '<div class="highlighted"><i class="fa fa-microphone message-icon" aria-hidden="true"></i><span> Audio</span></div>';
                                    } else if (data.result.last_message_type === 'revoked') {
                                        lastMessageHtml = '<div class="highlighted"><i class="fa fa-ban message-icon" aria-hidden="true"></i><span>Eliminaste este mensaje</span></div>';
                                    } else {
                                        lastMessageHtml = '<div class="highlighted"><span>' + (data.result.last_message_body.length > 35 ? data.result.last_message_body.substring(0, 35) + '...' : data.result.last_message_body) + '</span></div>';
                                    }
                                
                                    chatItem.find('.chat-info').append(lastMessageHtml);
                                }

                                // Añadir el chat a la sección de "Chats Pendientes"
                                $('.seccion-inferior').append(chatItem);

                                $('#message-input-container').hide(); 
                                showAttendButton(); 
                            }
                        },
                        error: function(xhr, status, error) {
                            console.error('Error al actualizar el estado del chat:', error);
                            Swal.fire({
                                title: 'Error!',
                                text: 'Hubo un problema al actualizar el estado del chat.',
                                icon: 'error',
                                confirmButtonText: 'Aceptar'
                            });
                        }
                    });
                } else {
                    $('#messages-container').hide(); 
                    showMessageInput();
                }
            });

            $(document).on('click', '.chat-ready-icon', function () {
                selectedChatId = $(this).data('chat-id');

                if (selectedChatId) {
                    showAttendButton(); 

                    $.ajax({
                        url: '/api/chat/update_status', 
                        type: 'POST',
                        headers: {
                            'X-CSRFToken': $('meta[name="csrf-token"]').attr('content'),
                            'Content-Type': 'application/json'
                        },
                        data: JSON.stringify({
                            chat_id: selectedChatId,
                            status_chat: 'atendido' 
                        }),
                        success: function(data) {
                            if(data.result && data.result.status === 'success'){

                                var chatItem = $('.chat-item[data-chat-id="' + selectedChatId + '"]');
                                chatItem.remove();  
                            }
                            $('#message-input-container').hide(); 
                            showAttendButton(); 
                        },
                        error: function(xhr, status, error) {
                            console.error('Error al actualizar el estado del chat:', error);
                            Swal.fire({
                                title: 'Error!',
                                text: 'Hubo un problema al actualizar el estado del chat.',
                                icon: 'error',
                                confirmButtonText: 'Aceptar'
                            });
                        }
                    });
                } else {
                    $('#messages-container').hide(); 
                    showMessageInput();
                }
            });

            $('#send-message-btn').on('click', function () {
                if (selectedChatId) {
                    var messageBody = $('#message-input').val();
                    if (messageBody.trim()) {
                        sendMessage(selectedChatId, messageBody);
                    }
                }
            });

            // ---------------------------------------- Agregar Contacto ----------------------------------------
            $(document).on('click', '.contact-plus-icon', function () {
                var name = $(this).closest('.contact-item').find('.contact-name').text();
                var phoneNumber = $(this).closest('.contact-item').find('.contact-phone').text();
                var profilePicUrl = $(this).closest('.contact-item').find('.profile-pic img').attr('src');
            
                $.ajax({
                    url: '/api/contact/add',
                    type: 'POST',
                    headers: {
                        'X-CSRFToken': $('meta[name="csrf-token"]').attr('content'),
                        'Content-Type': 'application/json'
                    },
                    data: JSON.stringify({
                        name: name,
                        phone_number: phoneNumber,
                        profile_pic_url: profilePicUrl
                    }),
                    success: function(data) {
                        if (data.result && data.result.status === 'success') {
                            Swal.fire({
                                title: 'Éxito!',
                                text: 'Contacto agregado exitosamente.',
                                icon: 'success',
                                confirmButtonText: 'Aceptar'
                            });
                        } else {
                            Swal.fire({
                                title: 'Advertencia!',
                                text: data.result.message || 'No se pudo agregar el contacto.',
                                icon: 'warning',
                                confirmButtonText: 'Aceptar'
                            });
                        }
                    },
                    error: function(xhr, status, error) {
                        Swal.fire({
                            title: 'Error!',
                            text: 'Error en la solicitud: ' + error,
                            icon: 'error',
                            confirmButtonText: 'Aceptar'
                        });
                    }
                });
            });        

            // ---------------------------------------- Obtener Chat por Contacto ----------------------------------------
            $(document).on('click', '.profile-pic', function () {
                var serialized = $(this).data('serialized');
                var userId = $(this).data('user-id');
                var phoneNumber = $(this).data('phone-number');
            
                $.ajax({
                    url: '/api/chat/id',
                    type: 'POST',
                    headers: {
                        'X-CSRFToken': $('meta[name="csrf-token"]').attr('content'),
                        'Content-Type': 'application/json'
                    },
                    data: JSON.stringify({
                        serialized: serialized,
                        user_id: userId,
                        phone_number: phoneNumber
                    }),
                    success: function(data) {
                        if (data.result && data.result.status === 'success') {
                            var chatId = data.result.chat_id;
                            selectedChatId = chatId;

                            window.chat_id_contact_section = data.result.chat_id;
                            window.contact_id_section = data.result.contact_id;
                            $('#messages-container').show();
                            loadMessages(selectedChatId);
                        } else {
                        }
                    },
                    error: function(xhr, status, error) {
                        console.error('Error en la solicitud:', error);
                    }
                });
            });

            // ---------------------------------------- Enviar Productos ----------------------------------------
            $(document).on('click', '.product-item', function () {
                const productId = $(this).data('product-id'); 
                const chatId = selectedChatId; 
            
                if (!chatId) {
                    console.log('No se ha seleccionado un chat.');
                    return;
                }

                // Verifica si el input está habilitado o si el botón de atender está visible
                if (window.currentChatStatus !== 'atendiendo' || window.currentAssignedUserId !== selectedSessionId) {
                    return;
                }
            
                var apiUrl = '/api/message/send-product';
                var csrfToken = $('meta[name="csrf-token"]').attr('content');

                $.ajax({
                    url: apiUrl,
                    type: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json'
                    },
                    data: JSON.stringify({
                        chat_id: chatId,
                        product_id: productId
                    }),
                    success: function(data) {
                        if (data.result && data.result.status === 'success') {
                            loadMessages(chatId);
                        } else {
                            console.error('Error al enviar el producto:', data.message);
                        }
                    },
                    error: function(xhr, status, error) {
                        console.error('Error en la solicitud:', error);
                    }
                });
            });

            // ---------------------------------------- Enviar Mensajes por defecto ----------------------------------------
            $(document).on('click', '.send-icon', function () {
                const defaultId = $(this).data('message-id'); 
                const chatId = selectedChatId; 
            
                if (!chatId) {
                    return;
                }

                // Verifica si el chat está en el estado de "atendiendo" y si está asignado al usuario actual
                if (window.currentChatStatus !== 'atendiendo' || window.currentAssignedUserId !== selectedSessionId) {
                    return;
                }
            
                var apiUrl = '/api/message/send-default-messages';
                var csrfToken = $('meta[name="csrf-token"]').attr('content');

                $.ajax({
                    url: apiUrl,
                    type: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json'
                    },
                    data: JSON.stringify({
                        chat_id: chatId,
                        default_id: defaultId
                    }),
                    success: function(data) {
                        if (data.status === 'success') {
                            loadMessages(chatId);
                        } else {
                            console.error('Error al enviar el mensaje por defecto:', data.message);
                        }
                    },
                    error: function(xhr, status, error) {
                        console.error('Error en la solicitud:', error);
                    }
                });
            });

            // ---------------------------------------- Menu de opciones (Mensaje) ----------------------------------------
            $(document).on('click', '.message-options-btn', function (e) {
                e.stopPropagation(); 
                var messageElement = $(this).closest('.message');
                var messageId = $(this).data('message-id')
                var indexmessage = $(this).data('message-index');
                var existingMenu = messageElement.find('.message-options-menu');
            
                // Verifica si el input está habilitado o si el botón de atender está visible
                if (window.currentChatStatus !== 'atendiendo' || window.currentAssignedUserId !== selectedSessionId) {
                    return;
                }else{
                    // Alternar la visibilidad del menú con cada clic
                    if (existingMenu.length) {
                        existingMenu.remove(); 
                    } else {
                        var optionsMenuHtml = '<div class="message-options-menu">';
                        optionsMenuHtml += '<ul>';
                        optionsMenuHtml += '<li><button class="reply-message" data-message-id="' + messageId + '" data-message-index="' + indexmessage + '" style="border: none; background: none; position: sticky;">Responder</button></li>';
                        if (messageElement.hasClass('from-me')) {
                            optionsMenuHtml += '<li><button class="delete-message" data-message-id="' + messageId + '" style="border: none; background: none;">Eliminar</button></li>';
                        }
                        optionsMenuHtml += '</ul>';
                        optionsMenuHtml += '</div>';
                
                        // Agregar el menú y posicionarlo
                        $(this).after(optionsMenuHtml);
                    }
                }
            });
            
            // Evento para eliminar el menú al hacer clic en cualquier lugar fuera del mensaje
            $(document).on('click', function (e) {
                $('.message-options-menu').remove();
            });
            
            $(document).on('mouseenter', '.message', function (e) {
                var messageElement = $(this);
                messageElement.find('.message-options-menu').show();
            });
            
            $(document).on('mouseleave', '.message', function (e) {
                var messageElement = $(this);
                messageElement.find('.message-options-menu').hide();
            }); 

            // ---------------------------------------- Responder Mensaje ----------------------------------------
            $(document).on('click', '.reply-message', function (e) {
                e.stopPropagation(); 
            
                if (selectedChatId) {
                    var messageId = $(this).data('message-id');
                    selectedMessageId = messageId
                    var indexmessage = $(this).data('message-index');
            
                    // Selecciona el mensaje correspondiente usando el índice
                    var $messageElement = $('#' + indexmessage);
            
                    if ($messageElement.length) {
                        let messageText = $messageElement.find('.text-message-body').html(); 
                        let fromName = $messageElement.hasClass('from-me') ? 'Tú' : $('.chat-banner .chat-name').text(); 
                        let messageType = $messageElement.data('message-type'); 

                        $('#reply-name').text(fromName);
                        let iconHtml = '';
                        switch (messageType) {
                            case 'image':
                                iconHtml = '<span><i class="fa fa-image" aria-hidden="true"></i> Imagen</span>';
                                $('#reply-text').html(iconHtml);
                                break;
                            case 'video':
                                iconHtml = '<span><i class="fa fa-video-camera" aria-hidden="true"></i> Video</span>';
                                $('#reply-text').html(iconHtml);
                                break;
                            case 'document':
                                iconHtml = '<span><i class="fa fa-file" aria-hidden="true"></i> Documento</span>';
                                $('#reply-text').html(iconHtml);
                                break;
                            case 'audio':
                                iconHtml = '<span><i class="fa fa-microphone" aria-hidden="true"></i> Audio</span>';
                                $('#reply-text').html(iconHtml);
                                break;
                            case 'groups_v4_invite':
                                iconHtml = '<span><i class="fa fa-users" aria-hidden="true"></i> Invitación de Grupo</span>';
                                $('#reply-text').html(iconHtml);
                                break;
                            case 'ptt':
                                iconHtml = '<span><i class="fa fa-microphone" aria-hidden="true"></i> Audio</span>';
                                $('#reply-text').html(iconHtml);
                                break;
                            case 'sticker':
                                iconHtml = '<span><i class="fa fa-sticky-note" aria-hidden="true"></i> Sticker</span>';
                                $('#reply-text').html(iconHtml);
                                break;
                            default:
                                $('#reply-text').html(messageText);
                                break;
                        }
                        
                        showReplyContainer(); 

                        // Almacena el ID del mensaje para usarlo al enviar la respuesta
                        $('#reply-container').data('reply-message-id', messageId);
                    } else {
                        console.error('No se encontró el mensaje con el índice especificado:', indexmessage);
                    }
                }
            });

            window.showReplyContainer = function(){
                updateScrollButtonPosition();
                const replyContainer = document.getElementById('reply-container');
                replyContainer.style.display = 'flex'; 
                setTimeout(() => {
                    replyContainer.classList.add('show'); 
                }, 10); 
            }
            
            window.hideReplyContainer = function(){
                updateScrollButtonPosition();
                const replyContainer = document.getElementById('reply-container');
                replyContainer.classList.remove('show'); 
                setTimeout(() => {
                    replyContainer.style.display = 'none';
                }, 300); 
            }
        
            // Evento para cancelar la respuesta
            $(document).on('click', '#cancel-reply-btn', function () {
                selectedMessageId = null;
                hideReplyContainer(); 
                $('#reply-text').text('');
                $('#reply-name').text('');
                $('#reply-container').removeData('reply-message-id');
            });    

            // ---------------------------------------- Eliminar Mensaje ----------------------------------------
            $(document).on('click', '.delete-message', function (e) {
                e.stopPropagation();
                if (selectedChatId) {

                    const chat_ID = selectedChatId
                    var messageId = $(this).data('message-id');
            
                    // Mostrar SweetAlert de confirmación
                    Swal.fire({
                        title: '¿Estás seguro?',
                        text: "Este mensaje será eliminado y no podrás deshacer esta acción.",
                        icon: 'warning',
                        showCancelButton: true,
                        confirmButtonColor: '#3085d6',
                        cancelButtonColor: '#d33',
                        confirmButtonText: 'Sí, eliminar',
                        cancelButtonText: 'Cancelar'
                    }).then((result) => {
                        if (result.isConfirmed) {
                            var apiUrl = '/api/message/delete';
                            var csrfToken = $('meta[name="csrf-token"]').attr('content');
            
                            $.ajax({
                                url: apiUrl,
                                type: 'POST',
                                headers: {
                                    'X-CSRFToken': csrfToken,
                                    'Content-Type': 'application/json'
                                },
                                data: JSON.stringify({
                                    message_id: messageId,
                                }),
                                success: function(data) {
                                    if (data.status === 'success') {
                                        loadMessages(chat_ID);
                                        Swal.fire({
                                            title: 'Eliminado!',
                                            text: 'El mensaje ha sido eliminado.',
                                            icon: 'success'
                                        });
                                    } else {
                                        console.error('Error al enviar el mensaje:', data.message);
                                        Swal.fire({
                                            title: 'Error!',
                                            text: 'No se pudo eliminar el mensaje.',
                                            icon: 'error'
                                        });
                                    }
                                },
                                error: function(xhr, status, error) {
                                    console.error('Error en la solicitud:', error);
                                    Swal.fire({
                                        title: 'Error!',
                                        text: 'No se pudo eliminar el mensaje.',
                                        icon: 'error'
                                    });
                                }
                            });
                        }
                    });
            
                    $('.message-options-menu').remove();
                }
            });

            $(document).on('click', '.save-contact-btn', function (e) {
                e.stopPropagation();
            
                var clientId = $(this).data('client-id');
                var contactPhone = $(this).data('contact-phone');
                var contactName = $(this).data('contact-name');
            
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
                        clientId: clientId,
                        contactNumber: contactPhone,
                        contactName: contactName
                    }),
                    success: function(data) {
                        if (data.result && data.result.status === 'success') {
                            Swal.fire({
                                title: 'Guardado!', 
                                text: 'El contacto ha sido guardado correctamente.', 
                                icon: 'success',
                                confirmButtonText: 'Aceptar'
                            }).then(() => {
                                // Verificar si el modal está abierto antes de ocultarlo
                                if (modal_contact.hasClass('show')) {
                                    modal_contact.modal('hide');
                                }
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
                    error: function(xhr, status, error) {
                        var errorMessage = xhr.responseJSON ? xhr.responseJSON.message : 'Error desconocido';
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

            // ---------------------------------------- Cargar/Obtener Mensajes ----------------------------------------
            window.loadMessages = function(chatId) {
                var apiUrl = '/api/messages/' + chatId;
                var csrfToken = $('meta[name="csrf-token"]').attr('content');
                window.currentChatId = chatId;

                $.ajax({
                    url: apiUrl,
                    type: 'GET',
                    headers: {
                        'X-CSRFToken': csrfToken
                    },
                    success: function(data) {
                        if (data && data.status === 'success') {
                            var chatBannerHtml = '<div class="chat-banner">';
                            chatBannerHtml += '<img class="chat-profile-pic" src="' + (data.chat.profile_pic_url || 'default-profile-pic-url') + '" alt="Profile Picture">';
                            chatBannerHtml += '<span class="chat-name">' + (data.chat.name || 'Desconocido') + '</span>';
                            chatBannerHtml += '</div>';
            
                            var messagesHtml = '';
                            var isGroupChat = data.chat.is_group;
                            var memberPhones = data.chat.member_phones;

                            data.messages.forEach(function(msg, index) {
                                var messageClass = msg.from_Me ? 'from-me' : 'from-them';
            
                                var originalDate = new Date(msg.timestamp);
                                originalDate.setHours(originalDate.getHours() - 5);
                                var timestamp = originalDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            
                                var messageId = 'message-' + index;
                                var id_message = msg.id;
            
                                var quotedMessageHtml = '';
                                if (msg.hasQuotedMsg) {
                                    var quotedMessageContent = '';
            
                                    switch (msg.quoted_type) {
                                        case 'image':
                                            quotedMessageContent = '<i class="fa fa-image message-icon" aria-hidden="true"></i><span> Imagen</span>';
                                            break;
                                        case 'video':
                                            quotedMessageContent = '<i class="fa fa-video-camera message-icon" aria-hidden="true"></i><span> Video</span>';
                                            break;
                                        case 'sticker':
                                            quotedMessageContent = '<i class="fa fa-sticky-note message-icon"></i><span> Sticker</span>';
                                            break;
                                        case 'ptt':
                                            quotedMessageContent = '<i class="fa fa-microphone message-icon" aria-hidden="true"></i><span> Audio</span>';
                                            break;
                                        case 'audio':
                                            quotedMessageContent = '<i class="fa fa-microphone message-icon" aria-hidden="true"></i><span> Audio</span>';
                                            break;
                                        case 'groups_v4_invite':
                                            quotedMessageContent = '<i class="fa fa-users message-icon" aria-hidden="true"></i><span> Invitación de Grupo</span>';
                                            break;
                                        case 'document':
                                            quotedMessageContent = '<i class="fa fa-file message-icon" aria-hidden="true"></i><span> Documento</span>';
                                            break;
                                        case 'vcard':
                                            quotedMessageContent = '<i class="fa fa-address-card message-icon" aria-hidden="true"></i><span> Contacto</span>';
                                            break;
                                        case 'location':
                                            quotedMessageContent = '<i class="fa fa-map-marker message-icon" aria-hidden="true"></i><span> Ubicación</span>';
                                            break;
                                        case 'chat':
                                            quotedMessageContent = msg.quoted_body || 'Sin contenido';
                                            break;
                                        default:
                                            quotedMessageContent = 'Sin contenido';
                                            break;
                                    }
            
                                    quotedMessageHtml = '<div class="quoted-message ' + messageClass + '">';
                                    quotedMessageHtml += '<span class="quoted-message-body">' + quotedMessageContent + '</span>';
                                    quotedMessageHtml += '</div>';
                                }

                                // Obtener el número de teléfono del 'serialized' del mensaje
                                var serializedParts = msg.serialized.split('_');
                                var senderPhone = isGroupChat && serializedParts.length > 0 ? serializedParts[serializedParts.length - 1].split('@')[0] : '';

                                // Si es un chat grupal, mostrar el número de teléfono del miembro
                                var memberInfo = '';
                                if (isGroupChat && senderPhone) {
                                    var lastNineDigits = senderPhone.slice(-9); 
                                    memberInfo = '0' + lastNineDigits; 
                                }
            
                                messagesHtml += '<div id="' + messageId + '" class="message ' + messageClass + '" data-message-type="' + msg.type + '">';
                                if (isGroupChat && memberInfo) {
                                    messagesHtml += '<span class="message-member-name">' + memberInfo + '</span>';
                                }
                                messagesHtml += '<span class="message-timestamp">' + timestamp + '</span>';
                                messagesHtml += '<button class="message-options-btn" data-message-id="' + id_message + '" data-message-index="' + messageId + '" data-message-type="' + msg.type + '"><i class="fa fa-chevron-down"></i></button>';
            
                                switch (msg.type) {
                                    case 'sticker':
                                        if (msg.media_data) {
                                            var mediaDataUrl = msg.media_data;
                                            messagesHtml += '<p class="message-body">' + quotedMessageHtml + '<img src="' + mediaDataUrl + '" alt="Sticker" class="message-media-sticker"></p>';
                                        } else {
                                            messagesHtml += '<p class="message-body">' + quotedMessageHtml + '<i class="fa fa-sticky-note message-icon"></i><span> Sticker</span></p>';
                                        }
                                        break;
                                    case 'location':
                                        if (msg.latitude) {
                                            var latitude = msg.latitude;
                                            var longitude = msg.longitude;
                                            var locationUrl = `https://www.google.com/maps?q=${latitude},${longitude}`;

                                            messagesHtml += '<p class="message-body">' + quotedMessageHtml;
                                            messagesHtml += '<div class="location-container">';
                                            messagesHtml += '<a href="' + locationUrl + '" target="_blank" class="location-link">';
                                            messagesHtml += '<div class="location-details">';
                                            messagesHtml += '<i class="fa fa-map-marker location-icon" aria-hidden="true"></i>';
                                            messagesHtml += '<span class="location-coordinates">Lat: ' + latitude + ', Long: ' + longitude + '</span>';
                                            messagesHtml += '</div>';
                                            messagesHtml += '</a>';
                                            messagesHtml += '</div>';
                                            messagesHtml += '</p>';
                                        } else {
                                            messagesHtml += '<p class="message-body">' + quotedMessageHtml + '<i class="fa fa-map-marker message-icon"></i><span> Ubicación</span></p>';
                                        }
                                        break;
                                    case 'image':
                                        if (msg.media_data) {
                                            var mediaDataUrl = msg.media_data;
                                            messagesHtml += '<p class="message-body">' + quotedMessageHtml + '<img src="' + mediaDataUrl + '" alt="Image" class="message-media-img">';
                                            if (msg.body) {
                                                messagesHtml += '<span class="text-message-body-img">' + convertToLink(msg.body) + '</span>';
                                            }
                                            messagesHtml += '</p>';
                                        } else {
                                            messagesHtml += '<p class="message-body">' + quotedMessageHtml + '<i class="fa fa-image message-icon" aria-hidden="true"></i><span> Imagen</span></p>';
                                        }
                                        break;
                                    case 'vcard':
                                        var vcardData = msg.body;
                                        var nameMatch = vcardData.match(/FN:(.+)/);

                                        var phoneRegexes = [
                                            /TEL(;type=[A-Z]+)?(;waid=\d+)?:(.+)/, // Captura el formato con 'type' y 'waid'
                                            /item\d+.TEL(;waid=\d+)?:(.+)/,
                                            /TEL;waid=\d+:(.+)/,
                                            /TEL:(.+)/,
                                            /item\d+.TEL:(.+)/,
                                            /TEL;type=CELL:(.+)/,
                                            /item1.TEL:(.+)/
                                        ];
                                    
                                        var contactPhone = 'Teléfono desconocido';
                                        for (var i = 0; i < phoneRegexes.length; i++) {
                                            var phoneMatch = vcardData.match(phoneRegexes[i]);
                                            if (phoneMatch) {
                                                contactPhone = phoneMatch[3] ? phoneMatch[3].trim() : phoneMatch[2].trim();
                                                break;
                                            }
                                        }

                                        var cleanedContactPhone = contactPhone.replace(/[\s+]/g, '');
                                        var contactName = nameMatch ? nameMatch[1].trim() : 'Nombre desconocido';

                                        messagesHtml += '<p class="message-body">' + quotedMessageHtml + '';
                                        messagesHtml += '<div class="vcard-container">';
                                        messagesHtml += '<i class="fa fa-user-circle contact-icon" aria-hidden="true"></i>';
                                        messagesHtml += '<div class="contact-info">';
                                        messagesHtml += '<span class="contact-name">' + contactName + '</span>';
                                        messagesHtml += '<span class="contact-phone">' + contactPhone + '</span>';
                                        messagesHtml += '<button class="save-contact-btn" data-client-id="' + data.chat.user_id + '" data-contact-phone="' + cleanedContactPhone + '" data-contact-name="' + contactName + '">Añadir Contacto</button>';
                                        messagesHtml += '</div>';
                                        messagesHtml += '</div>';
                                        messagesHtml += '</p>';
                                        break;

                                    case 'document':
                                        if (msg.media_temp_url) {
                                            var mediaDataUrl = msg.media_temp_url;
                                            messagesHtml += '<p class="message-body">' + quotedMessageHtml + 
                                                            '<a href="' + mediaDataUrl + '" target="_blank" download="document">' + 
                                                            '<i class="fa fa-file message-icon" aria-hidden="true"></i>' + 
                                                            '<span> Documento</span></a>';
                                            if (msg.body) {
                                                messagesHtml += '<span class="text-message-body-img">' + convertToLink(msg.body) + '</span>';
                                            }
                                            messagesHtml += '</p>';
                                        } else {
                                            messagesHtml += '<p class="message-body">' + quotedMessageHtml + '<i class="fa fa-file message-icon" aria-hidden="true"></i><span> Documento</span>';
                                            if (msg.body) {
                                                messagesHtml += '<span class="text-message-body-img">' + convertToLink(msg.body) + '</span>';
                                            }
                                            messagesHtml += '</p>';
                                        }
                                        break;
                                    case 'video':
                                        if (msg.media_temp_url) {
                                            var mediaTempUrl = msg.media_temp_url;
                                            messagesHtml += '<p class="message-body">' + quotedMessageHtml + '';
                                            messagesHtml += '<video controls width="90%">';
                                            messagesHtml += '<source src="' + mediaTempUrl + '" type="' + msg.media_mime_type + '">';
                                            messagesHtml += 'Your browser does not support the video tag.';
                                            messagesHtml += '</video>';
                                            if (msg.body) {
                                                messagesHtml += '<span class="text-message-body-img">' + convertToLink(msg.body) + '</span>';
                                            }
                                            messagesHtml += '</p>';
                                        } else {
                                            messagesHtml += '<p class="message-body">' + quotedMessageHtml + '<i class="fa fa-video-camera message-icon" aria-hidden="true"></i><span> Video</span>';
                                            if (msg.body) {
                                                messagesHtml += '<span class="text-message-body-img">' + convertToLink(msg.body) + '</span>';
                                            }
                                            messagesHtml += '</p>';
                                        }
                                        break;
                                    case 'ptt':
                                        if (msg.media_data) {
                                            var mediaDataUrl = msg.media_data;
                                            messagesHtml += '<p class="message-body">' + quotedMessageHtml + '<audio controls><source src="' + mediaDataUrl + '" type="' + msg.media_mime_type + '">Your browser does not support the audio element.</audio></p>';
                                        } else {
                                            messagesHtml += '<p class="message-body">' + quotedMessageHtml + '<i class="fa fa-microphone message-icon" aria-hidden="true"></i><span> Audio</span></p>';
                                        }
                                        break;
                                    case 'audio':
                                        if (msg.media_data) {
                                            var mediaDataUrl = msg.media_data;
                                            messagesHtml += '<p class="message-body">' + quotedMessageHtml + '<audio controls><source src="' + mediaDataUrl + '" type="' + msg.media_mime_type + '">Your browser does not support the audio element.</audio></p>';
                                        } else {
                                            messagesHtml += '<p class="message-body">' + quotedMessageHtml + '<i class="fa fa-microphone message-icon" aria-hidden="true"></i><span> Audio</span></p>';
                                        }
                                        break;
                                    case 'revoked':
                                        messagesHtml += '<p class="message-body">' + quotedMessageHtml + '<i class="fa fa-ban message-icon" aria-hidden="true"></i><span> Se elimino este mensaje</span></p>';
                                        break;
                                    default:
                                        messagesHtml += '<p class="message-body">' + quotedMessageHtml + '<span class="text-message-body">' + (convertToLink(msg.body)|| 'Sin contenido') + '</span></p>';
                                        break;
                                }
                                messagesHtml += '</div>';
                            });
            
                            var $messagesContainer = $('#messages-container .chat-messages');
                            var $chatBannerContainer = $('.chat-banner-container');
            
                            loadImages();
            
                            $chatBannerContainer.html(chatBannerHtml);
                            $messagesContainer.html(messagesHtml).show();
            
                            var lastMessage = $messagesContainer.find('.message').last();
                            if (lastMessage.length) {
                                $messagesContainer.scrollTop(lastMessage.offset().top - $messagesContainer.offset().top + $messagesContainer.scrollTop());
                            }

                            // Ajuste del estado del chat y el ID del usuario asignado
                            var chatStatus = data.chat.status;
                            var assignedUserId = data.chat.assigned_user_id;

                            // Guardar el estado del chat y el ID del usuario asignado en variables globales o algún lugar accesible
                            window.currentChatStatus = chatStatus;
                            window.currentAssignedUserId = assignedUserId;
            
                            // Verifica el estado del chat y muestra la sección correspondiente
                            if (data.chat.status === 'atendiendo' && data.chat.assigned_user_id === selectedSessionId) {
                                showMessageInput();
                            } else if (data.chat.status === 'atendiendo' && data.chat.assigned_user_id !== selectedSessionId) {
                                showInputDisabled(); 
                            } else {
                                showAttendButton(); 
                            }
            
                        } else {
                            if (data && data.status === 'error') {
                                var chatBannerHtmlError = '<div class="chat-banner">';
                                if (data.chat_info.name) {
                                    chatBannerHtmlError += '<img class="chat-profile-pic" src="' + (data.chat_info.profile_pic_url || 'https://cdn.playbuzz.com/cdn/913253cd-5a02-4bf2-83e1-18ff2cc7340f/c56157d5-5d8e-4826-89f9-361412275c35.jpg') + '" alt="Profile Picture">';
                                    chatBannerHtmlError += '<span class="chat-name">' + (data.chat_info.name || 'Desconocido') + '</span>';
                                } else {
                                    chatBannerHtmlError += '<img class="chat-profile-pic" src="https://cdn.playbuzz.com/cdn/913253cd-5a02-4bf2-83e1-18ff2cc7340f/c56157d5-5d8e-4826-89f9-361412275c35.jpg" alt="Profile Picture">';
                                    chatBannerHtmlError += '<span class="chat-name">Desconocido</span>';
                                }
                                chatBannerHtmlError += '</div>';
                                selectedChatId = data.chat_info.id;

                                var $chatBannerContainer = $('.chat-banner-container');
                                $chatBannerContainer.html(chatBannerHtmlError);
                                $('#messages-container .chat-messages').html('<p>No se encontraron mensajes.</p>').show();

                                if (data.chat_info.status === 'atendiendo' && data.chat_info.assigned_user_id === selectedSessionId) {
                                    showMessageInput();
                                } else if (data.chat_info.status === 'atendiendo' && data.chat_info.assigned_user_id !== selectedSessionId) {
                                    showInputDisabled(); 
                                } else {
                                    showAttendButton(); 
                                }
                            }
                        }
                    },
                    error: function(xhr, status, error) {
                        console.error('AJAX error:', error);
                        $('#chat-banner-container').html('<p>Hubo un error al cargar los mensajes.</p>');
                        $('#messages-container .chat-messages').html('<p>No se pudieron cargar los mensajes.</p>').show(); 
                    }
                });
            };

            // Función para detectar enlaces y convertirlos en hipervínculos
            function convertToLink(text) {
                var urlPattern = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
                return text.replace(urlPattern, function(url) {
                    return '<a href="' + url + '" target="_blank">' + url + '</a>';
                });
            }
            
            // ---------------------------------------- Scrool Button ----------------------------------------
            window.messagesContainer = $('#messages-container .chat-messages');
            window.scrollToBottomBtn = $('#scroll-to-bottom');

            // Mostrar u ocultar el botón de desplazamiento hacia abajo
            window.messagesContainer.on('scroll', function() {
                if (window.messagesContainer.scrollTop() + window.messagesContainer.innerHeight() < window.messagesContainer[0].scrollHeight - 100) {
                    window.scrollToBottomBtn.fadeIn();
                } else {
                    window.scrollToBottomBtn.fadeOut();
                }
            });

            // Desplazar al fondo al hacer clic en el botón
            window.scrollToBottomBtn.on('click', function() {
                window.messagesContainer.scrollTop(window.messagesContainer[0].scrollHeight);
            });

            window.updateScrollButtonPosition = function(){
                if ($('#reply-container').is(':visible')) {
                    window.scrollToBottomBtn.css('bottom', '80px');
                } else {
                    window.scrollToBottomBtn.css('bottom', '170px');
                }
            }

            // ---------------------------------------- Enviar Mensajes ENTER (Input) ----------------------------------------
            const messageInput = document.getElementById('message-input');
            
            if (messageInput) {
                messageInput.addEventListener('keydown', function(event) {
                    if (event.key === 'Tab') {
                        event.preventDefault(); 
                    }
                });

                messageInput.addEventListener('keypress', function(event) {
                    if (event.key === 'Enter' && messageInput.value.trim() !== '') {
                        event.preventDefault();
                        const chatId = selectedChatId;
                        const replyMessageId = selectedMessageId
                        
                        if (chatId) {
                            if (replyMessageId) {
                                sendReplyMessage(chatId, messageInput.value.trim(), replyMessageId);
                            } else if(window.selectedMessageId_received) {
                                sendReplyMessageReceived(chatId, messageInput.value.trim(), window.selectedMessageId_received);
                            } else{
                                sendMessage(chatId, messageInput.value.trim());
                            }
                            messageInput.value = ''; 
                        }
                    }
                });
            }

            // ---------------------------------------- CTRL + V (Input) ----------------------------------------
            messageInput.addEventListener('paste', function(event) {
                const items = (event.clipboardData || event.originalEvent.clipboardData).items;
                let isFile = false;
            
                for (let index in items) {
                    const item = items[index];
                    if (item.kind === 'file') {
                        event.preventDefault();
            
                        const blob = item.getAsFile();
                        handlePastedFile(blob); 
                        isFile = true;
                        break; 
                    }
                }
            
                if (!isFile) {
                    // Deja que el evento siga su curso normal y se pegue como texto
                    setTimeout(() => {
                        messageInput.value += event.clipboardData.getData('Text'); 
                    }, 0);
                }
            });

            function handlePastedFile(file) {
                const fileType = file.type.split('/')[0];
                selectedFile = file;
        
                if (fileType === 'image' || fileType === 'video') {
                    previewImageOrVideo(file);
                } else {
                    previewDocumentFile(file);
                }
            }
        
            // ---------------------------------------- Arrastrar y Soltar (Input) ----------------------------------------
            const dropArea = document.getElementById('message-input');
            window.addEventListener('dragover', (event) => event.preventDefault());
            window.addEventListener('drop', (event) => event.preventDefault());

            dropArea.addEventListener('dragover', (event) => {
                event.preventDefault();
                dropArea.classList.add('drag-over'); 
            });
            
            dropArea.addEventListener('dragleave', () => {
                dropArea.classList.remove('drag-over'); 
            });
            
            dropArea.addEventListener('drop', (event) => {
                event.preventDefault();
                dropArea.classList.remove('drag-over');
                
                const items = event.dataTransfer.items;
                let isFile = false;
                
                for (let index in items) {
                    const item = items[index];
                    if (item.kind === 'file') {
                        const blob = item.getAsFile();
                        handlePastedFile(blob);
                        isFile = true;
                        break;
                    }
                }
                
                if (!isFile) {
                    console.log('No se soltó un archivo.');
                }
            });

            $('#send-message-btn').on('click', function () {
                const chatId = selectedChatId;
                const messageBody = $('#message-input').val().trim();
        
                if (selectedFile) {
                    sendFile(chatId, selectedFile, messageBody);
                } 
            });

            // ---------------------------------------- Enviar Mensajes (Input) ----------------------------------------
            function sendMessage(chatId, messageBody) {
                var apiUrl = '/api/message/send';
                var csrfToken = $('meta[name="csrf-token"]').attr('content');
            
                $.ajax({
                    url: apiUrl,
                    type: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json'
                    },
                    data: JSON.stringify({
                        chat_id: chatId,
                        message_body: messageBody
                    }),
                    success: function(data) {
                        if (data.status === 'success') {
                            setTimeout(function() {
                                loadMessages(chatId);
                            }, 500);
                        } else {
                            console.error('Error al enviar el mensaje:', data.message);
                        }
                    },
                    error: function(xhr, status, error) {
                        console.error('Error en la solicitud:', error);
                    }
                });
            }

            function sendReplyMessage(chatId, messageBody, replyMessageId) {
                var apiUrl = '/api/message/reply';
                var csrfToken = $('meta[name="csrf-token"]').attr('content');
            
                $.ajax({
                    url: apiUrl,
                    type: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json'
                    },
                    data: JSON.stringify({
                        chat_id: chatId,
                        message_id: replyMessageId,
                        reply: messageBody
                    }),
                    success: function (data) {
                        if (data.status === 'success') {
                            setTimeout(function() {
                                loadMessages(chatId);
                            }, 500);
                            hideReplyContainer(); 
                            $('#reply-text').text('');
                            $('#reply-name').text('');
                            $('#reply-container').removeData('reply-message-id');
                            selectedMessageId = null; 
                        } else {
                            console.error('Error al responder el mensaje:', data.message);
                        }
                    },
                    error: function (xhr, status, error) {
                        console.error('Error en la solicitud:', error);
                    }
                });
            }  
            
            function sendReplyMessageReceived(chatId, messageBody, replyMessageId) {
                var apiUrl = '/api/message/reply-received';
                var csrfToken = $('meta[name="csrf-token"]').attr('content');
            
                $.ajax({
                    url: apiUrl,
                    type: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json'
                    },
                    data: JSON.stringify({
                        chat_id: chatId,
                        message_id: replyMessageId,
                        reply: messageBody
                    }),
                    success: function (data) {
                        if (data.status === 'success') {
                            setTimeout(function() {
                                loadMessages(chatId);
                            }, 500);
                            hideReplyContainer(); 
                            $('#reply-text').text('');
                            $('#reply-name').text('');
                            $('#reply-container').removeData('reply-message-id');
                            window.selectedMessageId_received = null; 
                        } else {
                            console.error('Error al responder el mensaje:', data.message);
                        }
                    },
                    error: function (xhr, status, error) {
                        console.error('Error en la solicitud:', error);
                    }
                });
            }   
        });

        

        // ---------------------------------------- LightBox (Imagenes) ----------------------------------------
        var images = [];
        var currentIndex = 0;

       // Cargar imágenes en el arreglo
        function loadImages() {
            images = [];
            $('.message-media-img').each(function(index, img) {
                var $message = $(img).closest('.message');
                var from = $message.hasClass('from-me') ? 'Tú' : $('.chat-banner .chat-name').text();
                var body = $message.find('.text-message-body-img').text() || '';
                images.push({
                    src: $(img).attr('src'),
                    timestamp: $message.find('.message-timestamp').text(),
                    from: from,
                    body: body
                });
            });
        }

        // Mostrar la imagen en el lightbox
        function showImage(index) {
            if (index >= 0 && index < images.length) {
                currentIndex = index;
                $('#lightbox-img').attr('src', images[index].src);
                $('#lightbox-info').text(images[index].from + ' - ' + images[index].timestamp);
                
                // Mostrar el texto del msg.body si existe
                if (images[index].body) {
                    $('#lightbox-text').text(images[index].body).show();
                } else {
                    $('#lightbox-text').hide();
                }
    
                $('#lightbox').fadeIn();
            }
        }

        $(document).on('click', '.message-media-img', function() {
            loadImages();
            var clickedSrc = $(this).attr('src');
            currentIndex = images.findIndex(img => img.src === clickedSrc);
            showImage(currentIndex);
        });

        $('#lightbox-close').on('click', function() {
            $('#lightbox').fadeOut();
        });

        $('#lightbox').on('click', function(e) {
            if (e.target === this) {
                $(this).fadeOut();
            }
        });

        // Navegación entre imágenes
        $('#prev-img').on('click', function(e) {
            e.stopPropagation();
            if (currentIndex > 0) {
                showImage(currentIndex - 1);
            }
        });

        // Navegación entre imágenes
        $('#next-img').on('click', function(e) {
            e.stopPropagation();
            if (currentIndex < images.length - 1) {
                showImage(currentIndex + 1);
            }
        });