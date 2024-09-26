
        $(document).ready(function () {
            const stickerBtn = document.getElementById('sticker-btn');
            const closeStickerPickerBtn = document.getElementById('close-sticker-picker');
            const stickerPicker = document.getElementById('sticker-picker');
            const stickerPickerBody = document.getElementById('sticker-picker-body');
            const emojiPicker = document.getElementById('emoji-picker');
            const plusPicker = document.getElementById('plus-picker');
            const plusBtn = document.getElementById('plus-btn');
            let selectedChatId = null;

            // Crear y configurar el elemento input file
            const stickerFileInput = document.createElement('input');
            stickerFileInput.type = 'file';
            stickerFileInput.id = 'sticker-file-input';
            stickerFileInput.accept = 'image/webp';
            stickerFileInput.style.display = 'none';
            document.body.appendChild(stickerFileInput);

            function closeAllPickers() {
                if (stickerPicker) {
                    stickerPicker.style.display = 'none';
                }
                if (emojiPicker) {
                    emojiPicker.style.display = 'none';
                }
                if (plusPicker){
                    plusPicker.style.display = 'none';
                }
                if (plusBtn) {
                    plusBtn.innerHTML = '<i class="fa fa-plus message-icon" aria-hidden="true"></i>'; // Cambia el icono a +
                }
            }

            $(document).on('click', function (e) {
                if (stickerPicker && !$(e.target).closest('#sticker-picker, #sticker-btn').length) {
                    stickerPicker.style.display = 'none';
                }
            });

            function loadStickers() {
                $.ajax({
                    url: '/api/sticker',
                    method: 'GET',
                    dataType: 'json',
                    success: function (data) {
                        if (Array.isArray(data)) {
                            if (stickerPickerBody) {
                                stickerPickerBody.innerHTML = '';

                                const addStickerDiv = document.createElement('div');
                                addStickerDiv.classList.add('sticker', 'sticker-image');
                                addStickerDiv.id = 'add-sticker-btn';

                                const addStickerIcon = document.createElement('i');
                                addStickerIcon.classList.add('fa', 'fa-plus', 'sticker-add-icon');
                                addStickerIcon.style.fontSize = '50px';

                                addStickerDiv.appendChild(addStickerIcon);
                                stickerPickerBody.appendChild(addStickerDiv);

                                if (addStickerDiv) {
                                    addStickerDiv.addEventListener('click', function () {
                                        stickerFileInput.click();
                                    });
                                }

                                data.forEach(function (sticker) {
                                    const stickerDiv = document.createElement('div');
                                    stickerDiv.classList.add('sticker');

                                    const stickerImg = document.createElement('img');
                                    stickerImg.src = sticker.sticker_url;
                                    stickerImg.alt = sticker.name;
                                    stickerImg.title = sticker.name;
                                    stickerImg.classList.add('sticker-image');

                                    const closeBtn = document.createElement('button');
                                    closeBtn.classList.add('sticker-close-btn');
                                    closeBtn.innerHTML = '<i class="fa fa-times"></i>';
                                    closeBtn.setAttribute('data-sticker-id', sticker.id);

                                    if (stickerImg) {
                                        stickerImg.addEventListener('click', function () {
                                            if (selectedChatId) {
                                                sendSticker(selectedChatId, sticker.sticker_url, sticker.file_name);
                                                if (stickerPicker) {
                                                    stickerPicker.style.display = 'none';
                                                }
                                            }
                                        });
                                    }

                                    if(closeBtn){
                                        closeBtn.addEventListener('click', function () {
                                            const stickerId = this.getAttribute('data-sticker-id');
                                    
                                            Swal.fire({
                                                title: '¿Estás seguro?',
                                                text: "¡No podrás revertir esto!",
                                                icon: 'warning',
                                                showCancelButton: true,
                                                confirmButtonColor: '#3085d6',
                                                cancelButtonColor: '#d33',
                                                confirmButtonText: 'Sí, eliminarlo',
                                                cancelButtonText: 'Cancelar'
                                            }).then((result) => {
                                                if (result.isConfirmed) {
                                                    $.ajax({
                                                        url: `/api/sticker/delete/${stickerId}`,
                                                        method: 'DELETE',
                                                        success: function (response) {
                                                            if (response.success) {
                                                                Swal.fire(
                                                                    'Eliminado',
                                                                    'El sticker ha sido eliminado.',
                                                                    'success'
                                                                ).then(() => {
                                                                    // Elimina el sticker del DOM
                                                                    $(`.sticker[data-sticker-id="${stickerId}"]`).remove();
                                                                    loadStickers(); 
                                                                });
                                                            } else {
                                                                Swal.fire(
                                                                    'Error',
                                                                    'Hubo un problema al eliminar el sticker: ' + response.error,
                                                                    'error'
                                                                );
                                                            }
                                                        },
                                                        error: function (xhr, status, error) {
                                                            Swal.fire(
                                                                'Error',
                                                                'Hubo un problema al eliminar el sticker: ' + xhr.responseText,
                                                                'error'
                                                            );
                                                        }
                                                    });
                                                }
                                            });
                                        });
                                    }

                                    stickerDiv.appendChild(stickerImg);
                                    stickerDiv.appendChild(closeBtn);
                                    stickerPickerBody.appendChild(stickerDiv);
                                });

                            }
                        }
                    },
                    error: function (xhr, status, error) {
                    }
                });
            }

            if (stickerBtn) {
                stickerBtn.addEventListener('click', function () {
                    if (stickerPicker.style.display === 'none' || stickerPicker.style.display === '') {
                        closeAllPickers(); // Cierra otros pickers antes de abrir el sticker picker
                        loadStickers();
                        stickerPicker.style.display = 'block';
                    } else {
                        stickerPicker.style.display = 'none';
                    }
                });
            }

            if (closeStickerPickerBtn) {
                closeStickerPickerBtn.addEventListener('click', function () {
                    stickerPicker.style.display = 'none';
                });
            }

            
            if (stickerFileInput) {
                stickerFileInput.addEventListener('change', function (event) {
                    const file = event.target.files[0];
                    if (file) {
                        const formData = new FormData();
                        formData.append('file', file);
                        formData.append('name', file.name.split('.')[0]);
                        formData.append('file_name', file.name);
                        formData.append('mime_type', file.type);
            
                        fetch('/api/sticker/create', {
                            method: 'POST',
                            body: formData
                        })
                        .then(response => {
                            if (!response.ok) {
                                return response.text().then(text => { throw new Error(text) });
                            }
                            return response.json();
                        })
                        .then(data => {
                            if (data.error) {
                                Swal.fire({
                                    title: 'Error',
                                    text: data.error,
                                    icon: 'error',
                                    confirmButtonText: 'Cerrar'
                                });
                            } else {
                                Swal.fire({
                                    title: 'Éxito',
                                    text: 'Sticker creado exitosamente',
                                    icon: 'success',
                                    confirmButtonText: 'Cerrar'
                                }).then((result) => {
                                    if (result.isConfirmed) {
                                        loadStickers();
                                    }
                                });
                            }
                        })
                        .catch(error => {
                            Swal.fire({
                                title: 'Error',
                                text: `Error al crear el sticker: ${error.message}`,
                                icon: 'error',
                                confirmButtonText: 'Cerrar'
                            });
                        });
                    }
                });
            }

            function sendSticker(chatId, stickerUrl, fileName) {
                $.ajax({
                    url: '/api/message/send-sticker',
                    method: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({
                        chat_id: chatId,
                        sticker_url: stickerUrl,
                        file_name: fileName
                    }),
                    success: function (data) {
                        if (data.status === 'success') {
                            if (typeof loadMessages === 'function') {
                                loadMessages(chatId);
                            }
                        }
                    },
                    error: function (xhr, status, error) {
                    }
                });
            }

            $(document).on('click', '.chat-item', function () {
                selectedChatId = $(this).data('chat-id');
            });
        });
