
        $(document).ready(function () {
            const plusBtn = document.getElementById('plus-btn');
            const closePlusPickerBtn = document.getElementById('close-plus-picker');
            const plusPicker = document.getElementById('plus-picker');
            const plusPickerBody = document.getElementById('plus-picker-body');

            const emojiPicker = document.getElementById('emoji-picker');
            const stickerPicker = document.getElementById('sticker-picker');

            const filePreview = document.getElementById('file-preview');
            const closeFilePreviewBtn = document.getElementById('close-file-preview');
            const previewImage = document.getElementById('preview-image');
            const previewVideo = document.getElementById('preview-video');
            const previewDocument = document.getElementById('preview-document');
            const fileMessage = document.getElementById('file-message');
            const sendFileBtn = document.getElementById('send-file');

            let selectedChatId = null;
            window.selectedFile = null;

            function closeAllPickers() {
                if (plusPicker) {
                    plusPicker.style.display = 'none';
                    plusBtn.innerHTML = '<i class="fa fa-plus message-icon" aria-hidden="true"></i>'; 
                }
                if (stickerPicker) {
                    stickerPicker.style.display = 'none';
                }
                if (emojiPicker) {
                    emojiPicker.style.display = 'none';
                }
                if (filePreview) {
                    toggleFilePreview(false); 
                }
            }

            function loadPlusOptions() {
                if (plusPickerBody) {
                    plusPickerBody.innerHTML = '';
        
                    const options = [
                        { id: 'photos-videos', icon: 'fa-camera', label: 'Fotos y Videos' },
                        { id: 'documents', icon: 'fa-file', label: 'Documentos' },
                    ];
        
                    options.forEach(function (option) {
                        const optionDiv = document.createElement('div');
                        optionDiv.classList.add('plus-option');
                        optionDiv.id = option.id;
        
                        const optionIcon = document.createElement('i');
                        optionIcon.classList.add('fa', option.icon, 'plus-option-icon');
                        optionDiv.appendChild(optionIcon);
        
                        const optionLabel = document.createElement('span');
                        optionLabel.classList.add('plus-option-label');
                        optionLabel.textContent = option.label;
                        optionDiv.appendChild(optionLabel);
        
                        plusPickerBody.appendChild(optionDiv);
        
                        optionDiv.addEventListener('click', function () {
                            if (option.id === 'photos-videos') {
                                handleFileSelection('image/*,video/*'); 
                            } else if (option.id === 'documents') {
                                handleFileSelection('*/*'); 
                            }
                        });
                    });
                }
            }

            function handleFileSelection(accept) {
                const fileInput = document.createElement('input');
                fileInput.type = 'file';
                fileInput.accept = accept;
                fileInput.style.display = 'none';
                document.body.appendChild(fileInput);
        
                fileInput.addEventListener('change', function (event) {
                    selectedFile = event.target.files[0];
                    if (accept === 'image/*,video/*') {
                        previewImageOrVideo(selectedFile);
                    } else {
                        previewDocumentFile(selectedFile);
                    }
                });
        
                fileInput.click();
            }
            

            window.previewImageOrVideo = function(file) {
                const fileType = file.type.split('/')[0];
                const fileUrl = URL.createObjectURL(file);
        
                previewImage.style.display = 'none';
                previewVideo.style.display = 'none';
                previewDocument.style.display = 'none';
        
                if (fileType === 'image') {
                    previewImage.src = fileUrl;
                    previewImage.style.display = 'block';
                } else if (fileType === 'video') {
                    previewVideo.src = fileUrl;
                    previewVideo.style.display = 'block';
                }
        
                toggleFilePreview(true);
            }

            window.previewDocumentFile = function(file) {
                previewImage.style.display = 'none';
                previewVideo.style.display = 'none';
                previewDocument.style.display = 'block';
        
                const fileType = file.type.split('/')[1];
                let iconClass = 'fa-file-alt'; 

                if (fileType === 'pdf') {
                    iconClass = 'fa-file-pdf-o';
                } else if (fileType.includes('word')) {
                    iconClass = 'fa-file-word-o';
                } else if (fileType.includes('excel')) {
                    iconClass = 'fa-file-excel-o';
                } else if (fileType.includes('powerpoint')) {
                    iconClass = 'fa-file-powerpoint-o';
                }

                previewDocument.innerHTML = `
                    <div class="document-preview">
                        <i class="fa ${iconClass} document-icon"></i>
                        <span class="document-name">${file.name}</span>
                    </div>
                `;

                toggleFilePreview(true);
            }

            window.sendFile = function(chatId, file, messageBody) {
                if (!file) {
                    console.error('No se seleccionó ningún archivo.');
                    return;
                }
        
                const fileName = file.name;
        
                const reader = new FileReader();
                reader.onload = function (e) {
                    const fileContent = e.target.result.split(',')[1]; 
        
                    $.ajax({
                        url: '/send_file_path',
                        method: 'POST',
                        contentType: 'application/json',
                        data: JSON.stringify({
                            chatId: chatId,
                            file_name: fileName,
                            file_content: fileContent,
                            messageBody: messageBody
                        }),
                        success: function (response) {
                            if (response.result && response.result.status === 'success') {
                                Swal.fire({
                                    icon: 'success',
                                    title: 'Éxito',
                                    text: 'Archivo enviado con éxito',
                                    confirmButtonText: 'Aceptar'
                                });
                                $('#preview-image').attr('src', '').hide();
                                $('#preview-video').attr('src', '').hide();
                                $('#preview-document').attr('src', '').hide();
                                $('#file-message').val('');
                                toggleFilePreview(false); 
                                if (typeof loadMessages === 'function') {
                                    loadMessages(chatId);
                                }
                            } else {
                                Swal.fire({
                                    icon: 'error',
                                    title: 'Error',
                                    text: 'Error al enviar archivo: ' + (response.result ? response.result.message : 'Error desconocido'),
                                    confirmButtonText: 'Aceptar'
                                });
                                $('#preview-image').attr('src', '').hide();
                                $('#preview-video').attr('src', '').hide();
                                $('#preview-document').attr('src', '').hide();
                                $('#file-message').val('');
                                toggleFilePreview(false); 
                                if (typeof loadMessages === 'function') {
                                    loadMessages(chatId);
                                }
                            }
                        },
                        error: function (xhr, status, error) {
                            Swal.fire({
                                icon: 'error',
                                title: 'Error',
                                text: 'Error al enviar archivo: ' + (xhr.responseText || error),
                                confirmButtonText: 'Aceptar'
                            });
                        }
                    });
                };
        
                reader.readAsDataURL(file); 
            }

            window.toggleFilePreview = function(visible) {
                const filePreview = $('#file-preview');
                if (visible) {
                    filePreview.css('display', 'flex');
                    filePreview.addClass('visible');
                } else {
                    filePreview.removeClass('visible');
                    
                    // Espera la animación antes de ocultarlo completamente
                    setTimeout(() => {
                        filePreview.css('display', 'none'); 
                    }, 300); 
                }
            };

            if (plusBtn) {
                plusBtn.addEventListener('click', function () {
                    if (plusPicker.style.display === 'none' || plusPicker.style.display === '') {
                        closeAllPickers(); 
                        loadPlusOptions();
                        plusPicker.style.display = 'block';
                        plusBtn.innerHTML = '<i class="fa fa-times message-icon" aria-hidden="true"></i>'; 
                    } else {
                        plusPicker.style.display = 'none';
                        plusBtn.innerHTML = '<i class="fa fa-plus message-icon" aria-hidden="true"></i>'; 
                    }
                });
            }
        
            if (closePlusPickerBtn) {
                closePlusPickerBtn.addEventListener('click', function () {
                    if (plusPicker) {
                        plusPicker.style.display = 'none';
                        plusBtn.innerHTML = '<i class="fa fa-plus message-icon" aria-hidden="true"></i>'; 
                    }
                });
            }
        
            if (closeFilePreviewBtn) {
                closeFilePreviewBtn.addEventListener('click', function () {
                    closeAllPickers();
                    plusPicker.style.display = 'none';
                    plusBtn.innerHTML = '<i class="fa fa-plus message-icon" aria-hidden="true"></i>';
                });
            }
        
            if (sendFileBtn) {
                sendFileBtn.addEventListener('click', function () {
                    const chatId = selectedChatId;
                    const messageBody = fileMessage.value;
        
                    sendFile(chatId, selectedFile, messageBody);
                });
            }
        
            $(document).on('click', '.chat-item', function () {
                selectedChatId = $(this).data('chat-id');
            });
        });