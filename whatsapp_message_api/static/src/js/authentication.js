
    $(document).ready(function () {
        
            const saveConnectionBtn = $('#save-connection');
            const phoneInput = $('#connection_phone_number');
            const countryCodeSelect = $('#country_code');

            document.querySelector('header').remove();
            document.querySelector('footer').remove();

            // Validar el formulario antes de enviar
            function validateForm() {
                const name = $('#connection_name').val().trim();
                const phoneNumber_form = phoneInput.val().trim();
                const color = $('#connection_color').val();
                const countryCode = $('#country_code').val();
                
                let isValid = true;

                // Validar campos vacíos
                if (!name || !phoneNumber_form || !color || !countryCode) {
                    Swal.fire({
                        icon: 'warning', 
                        title: 'Advertencia!',
                        text: 'Todos los campos requeridos.',
                        confirmButtonText: 'Aceptar'
                    });
                    isValid = false;
                }

                return isValid;
            }

            let ws; // WebSocket variable

            function updateQrCode(qrText) {
                const qrImg = document.getElementById("qr-code-div");
                if (!qrImg) {
                    console.error("Elemento 'qr-code-div' no encontrado.");
                    return;
                }
                qrImg.innerHTML = ""; // Limpia cualquier contenido previo
                new QRCode(qrImg, {
                    text: qrText,
                    correctLevel: QRCode.CorrectLevel.H
                });
            }

            // Función para abrir WebSocket con el número de teléfono dinámico
            function openWebSocket(phoneNumber) {
                if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
                    return;
                }

                ws = new WebSocket("ws://localhost:5000");

                ws.onopen = () => {
                    ws.send(JSON.stringify({ action: "subscribe", number: phoneNumber }));
                };

                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    const receivedNumber = String(data.number).trim();
                    const expectedNumber = String(phoneNumber).trim();

                    console.log('Mensaje recibido QR: ' + data.qr);
                    console.log('Mensaje recibido Numero: ' + receivedNumber);
                    console.log('Número esperado:', expectedNumber);

                    if (receivedNumber === expectedNumber && data.qr) {
                        updateQrCode(data.qr);
                    } else {
                        console.log('Número o QR no coinciden.');
                    }
                };

                ws.onclose = () => {
                    console.log("WebSocket closed");
                };

                ws.onerror = (event) => {
                    console.log("WebSocket error observed:", event);
                };
            }
            // Configurar eventos delegados para el modal QR
            $(document).on('click', '.open-modal-btn-qr', function () {
                var modal = document.getElementById('qr-modal');
                const phoneNumber = $(this).data('phone');

                if (modal) {
                    modal.style.display = 'block';
                    openWebSocket(phoneNumber);
                    fetchQRCode(phoneNumber);
                }
            });

            // Configurar evento para cerrar el modal
            $('.close-btn').on('click', function () {
                var modal = document.getElementById('qr-modal');
                if (modal) {
                    modal.style.display = 'none';
                    if (ws) {
                        ws.close(); // Cerrar WebSocket al cerrar el modal
                    }
                }
            });

            // Cerrar el modal cuando se hace clic fuera de él
            $(window).on('click', function (event) {
                var modal = document.getElementById('qr-modal');
                if (event.target === modal) {
                    modal.style.display = 'none';
                    if (ws) {
                        ws.close(); // Cerrar WebSocket al cerrar el modal
                    }
                }
            });

            // Función para configurar modales con CSS
            function setupCssModal(modalId, openBtnClass, closeBtnClass) {
                var modal = document.getElementById(modalId);
                var openBtns = document.querySelectorAll(openBtnClass);
                var closeBtn = document.querySelector(closeBtnClass);

                if (modal && openBtns.length > 0 && closeBtn) {
                    openBtns.forEach(function (openBtn) {
                        openBtn.onclick = function () {
                            modal.style.display = 'block';
                            const phoneNumber = $(this).data('phone');
                            openWebSocket(phoneNumber);
                            fetchQRCode(phoneNumber);
                        };
                    });

                    closeBtn.onclick = function () {
                        modal.style.display = 'none';
                        if (ws) {
                            ws.close(); // Cerrar WebSocket al cerrar el modal
                        }
                    };

                    window.onclick = function (event) {
                        if (event.target === modal) {
                            modal.style.display = 'none';
                            if (ws) {
                                ws.close(); // Cerrar WebSocket al cerrar el modal
                            }
                        }
                    };
                } else {
                }
            }

            
            // Función para configurar modales con Bootstrap
            function setupBootstrapModal(modalId, openBtnClass, closeBtnClass) {
                var modal = $('#' + modalId);
                var openBtn = $(openBtnClass);
                var closeBtn = $('#' + closeBtnClass);

                if (modal.length && openBtn.length && closeBtn.length) {
                    openBtn.on('click', function () {
                        if (navigator.appName == "Opera"){
                            modal.removeClass('fade');
                        }else {
                            modal.modal('show'); // Mostrar el modal usando Bootstrap
                        }
                    });

                    closeBtn.on('click', function () {
                        modal.modal('hide'); // Ocultar el modal usando Bootstrap
                    });

                    $(window).on('click', function (event) {
                        if ($(event.target).is(modal)) {
                            modal.modal('hide'); // Ocultar el modal usando Bootstrap
                        }
                    });
                } else {
                }
            }

            // Inicializa los modales CSS
            setupCssModal('qr-modal', '.open-modal-btn-qr', '.close-btn');
            // Inicializa los modales Bootstrap
            setupBootstrapModal('connection-modal', '.open-modal-btn-connection', 'close-modal-connection');

            function fetchQRCode(number) {
                fetch(`http://localhost:5000/api/qr/${number}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.qr) {
                            updateQrCode(data.qr);
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching QR code:', error);
                    });
            }

            saveConnectionBtn.on('click', function() {
                if (!validateForm()) {
                    return; // Detener la ejecución si el formulario no es válido
                }
            
                const name = $('#connection_name').val();
                const phone_Number = phoneInput.val();
                const color = $('#connection_color').val();
                const countryCode = countryCodeSelect.val(); // Obtener el código de país
                const fullNumber = countryCode + phone_Number;
            
                let formData = new FormData();
                formData.append('name', name);
                formData.append('phone_number', fullNumber);
                formData.append('color', color);
            
                $.ajax({
                    url: '/api/connection/add',
                    method: 'POST',
                    contentType: false,
                    processData: false,
                    data: formData,
                    success: function(response) {
                        if (response.success) {
                            Swal.fire({
                                title: 'Éxito',
                                text: 'Conexión creada exitosamente.',
                                icon: 'success',
                                confirmButtonText: 'Aceptar'
                            }).then((result) => {
                                if (result.isConfirmed) {
                                    // Agregar la nueva conexión al DOM
                                    $('.connections tbody').append(`
                                        <tr data-connection-id="${response.connection.id}">
                                            <td>${response.connection.id}</td>
                                            <td>${response.connection.name}</td>
                                            <td>${response.connection.phone_number}</td>
                                            <td><span class="color-box" style="background-color: ${response.connection.color}"></span></td>
                                            <td>
                                                <button class="open-modal-btn-qr" data-phone="${response.connection.phone_number}">
                                                    <i class="fa fa-qrcode" aria-hidden="true"></i>
                                                </button>
                                            </td>
                                            <td>
                                                <button class="open-modal-btn-delete" data-connection-id="${response.connection.id}">
                                                    <i class="fa fa-trash" aria-hidden="true"></i>
                                                </button>
                                            </td>
                                        </tr>
                                    `);

                                    // Limpiar los inputs del modal
                                    $('#connection_name').val('');
                                    $('#connection_phone_number').val('');
                                    $('#connection_color').val('');

                                    // Cerrar el modal
                                    $('#connection-modal').modal('hide');
                                }
                            });
                        } else {
                            Swal.fire({
                                title: 'Error',
                                text: 'Hubo un problema al crear la conexión: ' + response.message,
                                icon: 'error',
                                confirmButtonText: 'Aceptar'
                            });
                        }
                    },
                    error: function(xhr, status, error) {
                        let errorMessage = 'Error desconocido.';
                        if (xhr.responseJSON && xhr.responseJSON.message) {
                            errorMessage = xhr.responseJSON.message;
                        } else if (xhr.responseText) {
                            errorMessage = xhr.responseText;
                        }
            
                        Swal.fire({
                            title: 'Error',
                            text: 'Hubo un problema al crear la conexión: ' + errorMessage,
                            icon: 'error',
                            confirmButtonText: 'Aceptar'
                        });
                    }
                });
            });

            $('.connections').on('click', '.open-modal-btn-delete', function () {
                var connectionId = $(this).data('connection-id');

                Swal.fire({
                    title: '¿Estás seguro?',
                    text: "No podrás revertir esto!",
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#3085d6',
                    cancelButtonColor: '#d33',
                    confirmButtonText: 'Sí, eliminarla!',
                    cancelButtonText: 'Cancelar'
                }).then((result) => {
                    if (result.isConfirmed) {
                        $.ajax({
                            url: `/api/connection/delete/${connectionId}`,
                            method: 'POST',
                            success: function (response) {
                                // Eliminar el elemento del DOM
                                $(`tr[data-connection-id="${connectionId}"]`).remove();
                                Swal.fire({
                                    title: '¡Eliminado!',
                                    text:'La conexión ha sido eliminada.',
                                    icon:'success',
                                    confirmButtonText: 'Aceptar'
                                });
                            },
                            error: function (xhr, status, error) {
                                Swal.fire({
                                    title: 'Error',
                                    text: 'Hubo un problema al eliminar la conexión: ' + error,
                                    icon: 'error',
                                    confirmButtonText: 'Aceptar'
                                });
                            }
                        });
                    }
                });
            });
    });
