document.addEventListener('DOMContentLoaded', function () {
    const ws = new WebSocket('ws://127.0.0.1:5000');

    ws.onopen = function () {
        console.log('Conectado al servidor WebSocket');
    };

    ws.onmessage = function (event) {
        const data = JSON.parse(event.data);

        switch (data.eventType) {
            case 'authenticated':
                console.log('Cliente autenticado:', data.number);
                break;
            case 'ready':
                console.log('Cliente listo:', data.number);
                break;
            case 'message':
                const remoteId = data.data.message._data.id.remote;
                if (remoteId === 'status@broadcast') {
                    return;
                }
                if (remoteId.includes('@newsletter')) {
                    return;
                }
                sendMessageToOdoo(data.data.message, data.data.number, data.data.media);
                break;
            case 'disconnected':
                console.log(`Cliente desconectado: ${data.number}, Razón: ${data.reason}`);
                break;
        }
    };

    
    ws.onclose = function () {
        console.log('Desconectado del servidor WebSocket');
    };

    function sendMessageToOdoo(messageData, user, messageMedia) {
        $.ajax({
            url: '/api/chat/process_message', 
            type: 'POST',
            headers: {
                'X-CSRFToken': $('meta[name="csrf-token"]').attr('content'),
                'Content-Type': 'application/json'
            },
            data: JSON.stringify({
                from_serialized: messageData.from,
                to_serialized: messageData.to,
                body: messageData.body,
                timestamp: messageData.timestamp,
                messageType: messageData.type,
                user_phone_number : user,
                name_message: messageData._data.notifyName
            }),
            success: function(data) {
                if (data.result && data.result.status === 'success') {
                    const chatId = data.result.chat_id;
                    const unread_count = data.result.unread_count; 
                    const userAttendingId = data.result.user_attending_id;
                    window.user_id_message = data.result.user_id;

                        window.id_chat_received = chatId;
                        const chatItemMessage = $('.chat-item[data-chat-id="' + chatId + '"]');

                        if(chatId === window.currentChatId){
                            if (messageData.type !== 'chat') {
                                updateChatInterface(messageData, messageMedia);
                            }else{
                                updateChatInterface(messageData);
                            }
                        }
                        if(data.result.status_chat === 'atendiendo'){
                            if(userAttendingId === window.selectSessionUserId){
                                var audio = new Audio('/whatsapp_message_api/static/src/audio/phone-notification-100701.mp3'); // Reemplaza con la ruta correcta
                                audio.play().catch(error => {
                                    console.error('Error al reproducir el sonido:', error);
                                });
                                chatItemMessage.prependTo('.seccion-superior');
                            }
                        }else{
                            if (chatItemMessage.length > 0) {

                                const lastMessageElement = chatItemMessage.find('.chat-info .highlighted');
                                const unreadCountElement = chatItemMessage.find('.unread-count');

                                var audio = new Audio('/whatsapp_message_api/static/src/audio/phone-notification-100701.mp3'); // Reemplaza con la ruta correcta
                                audio.play().catch(error => {
                                    console.error('Error al reproducir el sonido:', error);
                                });

                                if (lastMessageElement.length > 0) {
                                    if (messageData.body.startsWith('https://') || messageData.body.startsWith('http://')) {
                                        lastMessageElement.html('<i class="fa fa-link message-icon" aria-hidden="true"></i><span>URL</span>');
                                    } else if (messageData.type === 'image') {
                                        lastMessageElement.html('<i class="fa fa-image message-icon" aria-hidden="true"></i><span>Imagen</span>');
                                    } else if (messageData.type === 'video') {
                                        lastMessageElement.html('<i class="fa fa-video-camera message-icon" aria-hidden="true"></i><span>Video</span>');
                                    } else if (messageData.type === 'groups_v4_invite') {
                                        lastMessageElement.html('<i class="fa fa-users message-icon" aria-hidden="true"></i><span>Invitación de Grupo</span>');
                                    } else if (messageData.type === 'location') {
                                        lastMessageElement.html('<i class="fa fa-map-marker message-icon" aria-hidden="true"></i><span>Ubicación</span>');
                                    } else if (messageData.type === 'sticker') {
                                        lastMessageElement.html('<i class="fa fa-sticky-note message-icon" aria-hidden="true"></i><span>Sticker</span>');
                                    } else if (messageData.type === 'document') {
                                        lastMessageElement.html('<i class="fa fa-file message-icon" aria-hidden="true"></i><span>Document</span>');
                                    } else if (messageData.type === 'ptt' || messageData.type === 'audio') {
                                        lastMessageElement.html('<i class="fa fa-microphone message-icon" aria-hidden="true"></i><span>Audio</span>');
                                    } else if (messageData.type === 'vcard'){
                                        lastMessageElement.html('<i class="fa fa-address-card message-icon" aria-hidden="true"></i><span> Contacto</span>');
                                    } else if (messageData.type === 'revoked') {
                                        lastMessageElement.html('<i class="fa fa-ban message-icon" aria-hidden="true"></i><span>Eliminaste este mensaje</span>');
                                    } else {
                                        lastMessageElement.text(messageData.body.length > 35 ? messageData.body.substring(0, 35) + '...' : messageData.body);
                                    }
                                } else {
                                    console.error('No se encontró el elemento <span> para actualizar el mensaje.');
                                }

                                if(unreadCountElement.length > 0) {
                                    unreadCountElement.text(unread_count);
                                }

                                chatItemMessage.prependTo('.seccion-inferior');
                            } else {
                                
                                var audio = new Audio('/whatsapp_message_api/static/src/audio/phone-notification-100701.mp3'); // Reemplaza con la ruta correcta
                                audio.play().catch(error => {
                                    console.error('Error al reproducir el sonido:', error);
                                });

                                let newChatItem = $('.seccion-inferior .chat-item:first').clone();
                                newChatItem.attr('data-chat-id', chatId);
                                newChatItem.find('.chat-name').text(data.result.name); 

                                const lastMessageElement = newChatItem.find('.highlighted');

                                if (messageData.body.startsWith('https://') || messageData.body.startsWith('http://')) {
                                    lastMessageElement.html('<i class="fa fa-link message-icon" aria-hidden="true"></i><span>URL</span>');
                                } else if (messageData.type === 'image') {
                                    lastMessageElement.html('<i class="fa fa-image message-icon" aria-hidden="true"></i><span>Imagen</span>');
                                } else if (messageData.type === 'video') {
                                    lastMessageElement.html('<i class="fa fa-video-camera message-icon" aria-hidden="true"></i><span>Video</span>');
                                } else if (messageData.type === 'groups_v4_invite') {
                                    lastMessageElement.html('<i class="fa fa-users message-icon" aria-hidden="true"></i><span>Invitación de Grupo</span>');
                                } else if (messageData.type === 'sticker') {
                                    lastMessageElement.html('<i class="fa fa-sticky-note message-icon" aria-hidden="true"></i><span>Sticker</span>');
                                } else if (messageData.type === 'location') {
                                    lastMessageElement.html('<i class="fa fa-map-marker message-icon" aria-hidden="true"></i><span>Ubicación</span>');
                                } else if (messageData.type === 'vcard'){
                                    lastMessageElement.html('<i class="fa fa-address-card message-icon" aria-hidden="true"></i><span> Contacto</span>');
                                }  else if (messageData.type === 'document') {
                                    lastMessageElement.html('<i class="fa fa-file message-icon" aria-hidden="true"></i><span>Document</span>');
                                } else if (messageData.type === 'ptt' || messageData.type === 'audio') {
                                    lastMessageElement.html('<i class="fa fa-microphone message-icon" aria-hidden="true"></i><span>Audio</span>');
                                } else if (messageData.type === 'revoked') {
                                    lastMessageElement.html('<i class="fa fa-ban message-icon" aria-hidden="true"></i><span>Eliminaste este mensaje</span>');
                                } else {
                                    lastMessageElement.text(messageData.body.length > 35 ? messageData.body.substring(0, 35) + '...' : messageData.body);
                                }

                                const defaultProfilePic = 'https://cdn.playbuzz.com/cdn/913253cd-5a02-4bf2-83e1-18ff2cc7340f/c56157d5-5d8e-4826-89f9-361412275c35.jpg';
                                const profilePicUrl = data.result.profile || defaultProfilePic;
                                newChatItem.find('.profile-pic img').attr('src', profilePicUrl);  

                                newChatItem.find('.unread-count').text(unread_count).show();

                                $('.seccion-inferior').prepend(newChatItem);
                            }
                        }
                } else {
                    console.error('Error al procesar el mensaje en Odoo:', data.result.message || 'Unknown error');
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error('Error en la solicitud AJAX a Odoo:', textStatus, errorThrown);
            }
        });
    }

    // ---------------------------------------- Menu de opciones (Mensaje) ----------------------------------------
    $(document).on('click', '.message-received-options-btn', function (e) {
        e.stopPropagation(); 
        var messageElement = $(this).closest('.message');
        var messageIdReceived = $(this).data('message-serialized')
        var messageTypeReceived = $(this).data('message-type')
        var messageBodyReceived = $(this).data('message-text')
        var existingMenu = messageElement.find('.message-received-options-menu');
    
        // Verifica si el input está habilitado o si el botón de atender está visible
        if (window.currentChatStatus !== 'atendiendo' || window.currentAssignedUserId !== window.selectSessionUserId) {
            return;
        }else{
            // Alternar la visibilidad del menú con cada clic
            if (existingMenu.length) {
                existingMenu.remove(); 
            } else {
                var optionsMenuHtml = '<div class="message-received-options-menu">';
                optionsMenuHtml += '<ul>';
                optionsMenuHtml += '<li><button class="reply-message-received" data-message-id="' + messageIdReceived + '" data-message-type="' + messageTypeReceived + '" data-message-text="' + messageBodyReceived + '" style="border: none; background: none; position: sticky;">Responder</button></li>';
                optionsMenuHtml += '</ul>';
                optionsMenuHtml += '</div>';
        
                // Agregar el menú y posicionarlo
                $(this).after(optionsMenuHtml);
            }
        }
    });

    // Evento para eliminar el menú al hacer clic en cualquier lugar fuera del mensaje
    $(document).on('click', function (e) {
        $('.message-received-options-menu').remove();
    });

    // ---------------------------------------- Responder Mensaje ----------------------------------------
    $(document).on('click', '.reply-message-received', function (e) {
        e.stopPropagation(); 
    
        if (window.selectedChat) {
            var messageSerialized = $(this).data('message-id');
            var typemessage = $(this).data('message-type');
            var textmessage = $(this).data('message-text');
    
            let fromName = '';
            window.selectedMessageId_received = messageSerialized;

            $('#reply-name').text(fromName);
            let iconHtml = '';
            switch (typemessage) {
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
                case 'ptt':
                    iconHtml = '<span><i class="fa fa-microphone" aria-hidden="true"></i> Audio</span>';
                    $('#reply-text').html(iconHtml);
                    break;
                case 'sticker':
                    iconHtml = '<span><i class="fa fa-sticky-note" aria-hidden="true"></i> Sticker</span>';
                    $('#reply-text').html(iconHtml);
                    break;
                case 'location':
                    iconHtml = '<span><i class="fa fa-map-marker" aria-hidden="true"></i> Ubicación</span>';
                    $('#reply-text').html(iconHtml);
                    break;
                case 'vcard':
                    iconHtml = '<span><i class="fa fa-address-card" aria-hidden="true"></i> Contacto</span>';
                    $('#reply-text').html(iconHtml);
                    break;
                case 'groups_v4_invite':
                    iconHtml = '<span><i class="fa fa-users" aria-hidden="true"></i> Invitación de Grupo</span>';
                    $('#reply-text').html(iconHtml);
                    break;
                default:
                    $('#reply-text').html(textmessage);
                    break;
                }
                
                showReplyContainer(); 

                // Almacena el ID del mensaje para usarlo al enviar la respuesta
                $('#reply-container').data('reply-message-id', messageSerialized);
        }
    });

    function updateChatInterface(messageData, messageMedia) {
        var currentChatId = window.currentChatId; 
        var messageChatId = window.id_chat_received;

        if (messageChatId && messageChatId === currentChatId) {

            var originalDate = new Date(messageData.timestamp * 1000); 
            originalDate.setHours(originalDate.getHours()); 
            var timestamp = originalDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            var messageClass = messageData.fromMe ? 'from-me' : 'from-them';

            var messageHtml = '<div id="' + messageData.id._serialized + '" class="message ' + messageClass + '"  data-message-type="' + messageData.type + '"  data-message-id="' + messageData.id._serialized + '">';
            messageHtml += '<span class="message-timestamp">' + timestamp + '</span>';
            messageHtml += '<button class="message-received-options-btn" data-message-serialized="' + messageData.id._serialized + '" data-message-type="' + messageData.type + '" data-message-text="' + messageData.body + '"><i class="fa fa-chevron-down"></i></button>';

            var quotedMessageHtml = '';
            if (messageData.hasQuotedMsg) {
                var quotedMessageContent = '';
                switch (messageData._data.quotedMsg.type) {
                    case 'image':
                        quotedMessageContent = '<i class="fa fa-image message-icon" aria-hidden="true"></i><span> Imagen</span>';
                        break;
                    case 'video':
                        quotedMessageContent = '<i class="fa fa-video-camera message-icon" aria-hidden="true"></i><span> Video</span>';
                        break;
                    case 'location':
                        quotedMessageContent = '<i class="fa fa-map-marker message-icon"></i><span> Ubicación</span>';
                        break;
                    case 'sticker':
                        quotedMessageContent = '<i class="fa fa-sticky-note message-icon"></i><span> Sticker</span>';
                        break;
                    case 'ptt':
                        quotedMessageContent = '<i class="fa fa-microphone message-icon" aria-hidden="true"></i><span> Audio</span>';
                        break;
                    case 'groups_v4_invite':
                        quotedMessageContent = '<i class="fa fa-users message-icon" aria-hidden="true"></i><span> Invitación de Grupo</span>';
                        break;
                    case 'audio':
                        quotedMessageContent = '<i class="fa fa-microphone message-icon" aria-hidden="true"></i><span> Audio</span>';
                        break;
                    case 'document':
                        quotedMessageContent = '<i class="fa fa-file message-icon" aria-hidden="true"></i><span> Documento</span>';
                        break;
                    case 'vcard':
                        quotedMessageContent = '<i class="fa fa-address-card message-icon" aria-hidden="true"></i><span> Contacto</span>';
                        break;
                    case 'chat':
                        quotedMessageContent = messageData._data.quotedMsg.body || 'Sin contenido';
                        break;
                    default:
                        quotedMessageContent = 'Sin contenido';
                        break;
                }

                quotedMessageHtml = '<div class="quoted-message ' + messageClass + '">';
                quotedMessageHtml += '<span class="quoted-message-body">' + quotedMessageContent + '</span>';
                quotedMessageHtml += '</div>';
            }

            // Función para detectar enlaces y convertirlos en hipervínculos
            function convertToLink(text) {
                var urlPattern = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
                return text.replace(urlPattern, function(url) {
                    return '<a href="' + url + '" target="_blank">' + url + '</a>';
                });
            }

            // Determinar el tipo de mensaje y formatear en consecuencia
            switch (messageData.type) {
                case 'sticker':
                    if (messageMedia && messageMedia.media.base64Data) {
                        var mediaDataUrl = 'data:' + messageMedia.media.mimetype + ';base64,' + messageMedia.media.base64Data;
                        messageHtml += '<p class="message-body">' + quotedMessageHtml + '<img src="' + mediaDataUrl + '" alt="Sticker" class="message-media-sticker"></p>';
                    } else {
                        messageHtml += '<p class="message-body">' + quotedMessageHtml + '<i class="fa fa-sticky-note message-icon"></i><span> Sticker</span></p>';
                    }
                    break;

                case 'location':
                    if (messageData.location) {
                        var latitude = messageData.location.latitude;
                        var longitude = messageData.location.longitude;
                        var locationUrl = `https://www.google.com/maps?q=${latitude},${longitude}`;

                        messageHtml += '<p class="message-body">' + quotedMessageHtml;
                        messageHtml += '<div class="location-container">';
                        messageHtml += '<a href="' + locationUrl + '" target="_blank" class="location-link">';
                        messageHtml += '<div class="location-details">';
                        messageHtml += '<i class="fa fa-map-marker location-icon" aria-hidden="true"></i>';
                        messageHtml += '<span class="location-coordinates">Lat: ' + latitude + ', Long: ' + longitude + '</span>';
                        messageHtml += '</div>';
                        messageHtml += '</a>';
                        messageHtml += '</div>';
                        messageHtml += '</p>';
                    } else {
                        messageHtml += '<p class="message-body">' + quotedMessageHtml + '<i class="fa fa-map-marker message-icon"></i><span> Ubicación</span></p>';
                    }
                    break;

                case 'vcard':
                    var vcardData = messageData.body;
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
                    var contactName = nameMatch ? nameMatch[1] : 'Nombre desconocido';

                    messageHtml += '<p class="message-body">' + quotedMessageHtml + '';
                    messageHtml += '<div class="vcard-container">';
                    messageHtml += '<i class="fa fa-user-circle contact-icon" aria-hidden="true"></i>';
                    messageHtml += '<div class="contact-info">';
                    messageHtml += '<span class="contact-name">' + contactName + '</span>';
                    messageHtml += '<span class="contact-phone">' + contactPhone + '</span>';
                    messageHtml += '<button class="save-contact-btn" data-client-id="' + window.user_id_message + '" data-contact-phone="' + cleanedContactPhone + '" data-contact-name="' + contactName + '">Añadir Contacto</button>';
                    messageHtml += '</div>';
                    messageHtml += '</div>';
                    messageHtml += '</p>';
                    break;

                case 'image':
                    if (messageMedia && messageMedia.media.base64Data) {
                        var mediaDataUrl = 'data:' + messageMedia.media.mimetype + ';base64,' + messageMedia.media.base64Data;
                        messageHtml += '<p class="message-body">' + quotedMessageHtml + '<img src="' + mediaDataUrl + '" alt="Image" class="message-media-img">';
                        if (messageData.body) {
                            messageHtml += '<span class="text-message-body-img">' + convertToLink(messageData.body) + '</span>';
                        }
                        messageHtml += '</p>';
                    } else {
                        messageHtml += '<p class="message-body">' + quotedMessageHtml + '<i class="fa fa-image message-icon" aria-hidden="true"></i><span> Imagen</span></p>';
                    }
                    break;

                case 'document':
                    if (messageMedia && messageMedia.media.base64Data) {
                        var mediaDataUrl = 'data:' + messageMedia.media.mimetype + ';base64,' + messageMedia.media.base64Data;
                        
                        messageHtml += '<p class="message-body">' + quotedMessageHtml + '<a href="' + mediaDataUrl + '" download="document"><i class="fa fa-file message-icon" aria-hidden="true"></i><span> Documento</span></a>';
                        if (messageData.body) {
                            messageHtml += '<span class="text-message-body-img">' + convertToLink(messageData.body) + '</span>';
                        }
                        messageHtml += '</p>';
                    } else {
                        messageHtml += '<p class="message-body">' + quotedMessageHtml + '<i class="fa fa-file message-icon" aria-hidden="true"></i><span> Documento</span>';
                        if (messageData.body) {
                            messageHtml += '<span class="text-message-body-img">' + convertToLink(messageData.body) + '</span>';
                        }
                        messageHtml += '</p>';
                    }
                    break;

                case 'video':
                    if (messageMedia && messageMedia.media.base64Data) {
                        var mediaDataUrl = 'data:' + messageMedia.media.mimetype + ';base64,' + messageMedia.media.base64Data;
                        messageHtml += '<p class="message-body">' + quotedMessageHtml + '';
                        messageHtml += '<video controls width="100%">';
                        messageHtml += '<source src="' + mediaDataUrl + '" type="' + messageMedia.media.mimetype + '">';
                        messageHtml += 'Your browser does not support the video tag.';
                        messageHtml += '</video>';
                        
                        if (messageData.body) {
                            messageHtml += '<span class="text-message-body-img">' + convertToLink(messageData.body) + '</span>';
                        }
                        
                        messageHtml += '</p>';
                    } else {
                        messageHtml += '<p class="message-body">' + quotedMessageHtml + '<i class="fa fa-video-camera message-icon" aria-hidden="true"></i><span> Video</span>';
                        if (messageData.body) {
                            messageHtml += '<span class="text-message-body-img">' + convertToLink(messageData.body) + '</span>';
                        }
                        messageHtml += '</p>';
                    }
                    break;

                case 'audio':
                case 'ptt': 
                    if (messageMedia && messageMedia.media.base64Data) {
                        var mediaDataUrl = 'data:' + messageMedia.media.mimetype + ';base64,' + messageMedia.media.base64Data;
                        messageHtml += '<p class="message-body">' + quotedMessageHtml + '<audio controls><source src="' + mediaDataUrl + '" type="' + messageMedia.media.mimetype + '">Your browser does not support the audio element.</audio></p>';
                    } else {
                        messageHtml += '<p class="message-body">' + quotedMessageHtml + '<i class="fa fa-microphone message-icon" aria-hidden="true"></i><span> Audio</span></p>';
                    }
                    break;

                case 'revoked':
                    messageHtml += '<p class="message-body"><i class="fa fa-ban message-icon" aria-hidden="true"></i><span> Este mensaje fue eliminado</span></p>';
                    break;

                default:
                    messageHtml += '<p class="message-body">' + quotedMessageHtml + '<span class="text-message-body">' + (convertToLink(messageData.body) || 'Sin contenido') + '</span></p>';
                    break;
            }

            messageHtml += '</div>';

            var $messagesContainer = $('#messages-container .chat-messages');
            $messagesContainer.append(messageHtml);

            var lastMessage = $messagesContainer.find('.message').last();
            if (lastMessage.length) {
                $messagesContainer.scrollTop(lastMessage.offset().top - $messagesContainer.offset().top + $messagesContainer.scrollTop());
            }
        }
    }

    function registerChatClickEvents() {
        const chatItems = document.querySelectorAll('.chat-item');
        chatItems.forEach((chatItem) => {
            chatItem.addEventListener('click', function () {
                window.currentChatId = chatItem.getAttribute('data-chat-id');
            });
        });
    }

    registerChatClickEvents();
});
