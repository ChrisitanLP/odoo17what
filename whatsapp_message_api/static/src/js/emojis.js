
        $(document).ready(function () {
            const emojiBtn = document.getElementById('emoji-btn');
            const closeEmojiPickerBtn = document.getElementById('close-emoji-picker');
            const emojiPicker = document.getElementById('emoji-picker');
            const emojiPickerBody = document.querySelector('.emoji-picker-body');
            const messageInput = document.getElementById('message-input');
        
            // Referencia al sticker picker para controlarlo
            const stickerPicker = document.getElementById('sticker-picker');
            const plusPicker = document.getElementById('plus-picker');
            const plusBtn = document.getElementById('plus-btn');

            function closeAllPickers() {
                if (emojiPicker) {
                    emojiPicker.style.display = 'none';
                }
                if (stickerPicker) {
                    stickerPicker.style.display = 'none';
                }
                if (plusPicker){
                    plusPicker.style.display = 'none';
                }
                if (plusBtn) {
                    plusBtn.innerHTML = '<i class="fa fa-plus message-icon" aria-hidden="true"></i>'; // Cambia el icono a +
                }
            }

            $(document).on('click', function (e) {
                if (emojiPicker && !$(e.target).closest('#emoji-picker, #emoji-btn').length) {
                    emojiPicker.style.display = 'none';
                }
            });

            // Verifica si los elementos existen y agrega eventos solo si están disponibles
            if (emojiBtn) {
                emojiBtn.addEventListener('click', function() {
                    if (emojiPicker.style.display === 'none' || emojiPicker.style.display === '') {
                        closeAllPickers(); // Cierra otros pickers antes de abrir el emoji picker
                        emojiPicker.style.display = 'block';
                    } else {
                        emojiPicker.style.display = 'none';
                    }
                });
            }
        
            if (closeEmojiPickerBtn) {
                closeEmojiPickerBtn.addEventListener('click', function() {
                    if (emojiPicker) {
                        emojiPicker.style.display = 'none';
                    }
                });
            }

            if (emojiPicker && emojiPickerBody && messageInput) {

                // Lógica para mostrar emojis
                const emojis = [
                    { section: 'Emoticonos', items: ['😊', '😂', '😍', '😒', '😘', '😎', '😡', '😍', '😗', '😜', '🤔', '😎', '😜', '🤗', '😄', '😆', '😅', '😩', '😢', '😲', '😰', '🥺', '😠', '😮', '😪', '😫', '😴', '😍', '😘', '😚', '😙', '🥳', '🤩', '😇', '🤔', '🙄', '😒', '🥺', '😭', '😈', '👿', '🙃', '🤯', '😤', '😣', '🤤', '🤪', '🤗', '😜', '😝', '😛', '😎', '🤑', '😲', '😳', '😱', '😨', '😰', '😢', '😥', '😓', '🤧', '🤯', '😵', '🤠', '😡', '😠', '😤', '😩', '😫', '😤', '😮', '😯', '😲'] }, 
                    { section: 'Actividades', items: ['⚽', '🏀', '🏈', '⚾', '🎾', '🏐', '🏉', '🎱', '🥅', '🏒', '🏑', '🏏', '🥎', '🎣', '🤿', '🎽', '🏆', '🏅', '🥇', '🥈', '🥉', '🎯', '🎳', '🎮', '🕹', '🎲', '♟', '🎯', '🎳', '🎩', '🎪', '🎭', '🃏', '🎴', '🀄', '🕹', '🎲', '🎰', '🧠', '🎬', '🎤', '🎧', '🎼', '🎹', '🥁', '🎺', '🎷', '🎸', '🎻', '🎵', '🎶', '🎼'] }, 
                    { section: 'Alimentos y bebidas', items: ['🍎', '🍏', '🍐', '🍊', '🍋', '🍌', '🍉', '🍇', '🍓', '🍈', '🍒', '🍑', '🍍', '🥭', '🥥', '🥝', '🍅', '🍆', '🥑', '🥒', '🥬', '🥦', '🥕', '🧄', '🧅', '🍠', '🥔', '🍯', '🥛', '🧃', '🧉', '🥤', '🍵', '☕', '🍶', '🍺', '🍻', '🥂', '🍷', '🥃', '🍸', '🍹', '🍾', '🥡', '🥢', '🍽', '🍴', '🥄', '🍳', '🥘', '🥗', '🍲', '🍜', '🍝', '🍞', '🥐', '🥯', '🍔', '🍟', '🍕', '🌭', '🍿', '🍩', '🍪', '🎂', '🍰', '🥧', '🍫', '🍬', '🍭', '🍮', '🍯', '🍰', '🧁'] }, 
                    { section: 'Personas', items: ['👶', '👧', '👦', '👩', '👨', '👴', '👵', '👶', '👸', '👳', '👲', '🧕', '🤴', '👸', '👷', '👮', '👯', '👼', '🤰', '🤱', '👩‍🔬', '👩‍🏫', '👩‍⚕️', '👩‍🍳', '👩‍🎓', '👩‍🚒', '👩‍✈️', '👩‍🚀', '👩‍⚖️', '🧑‍🧑', '👩‍🧑', '🧑‍🤝‍🧑', '👬', '👭', '👩‍❤️‍👩', '👩‍❤️‍👨', '👨‍❤️‍👨', '👨‍❤️‍👩', '👩‍❤️‍👩', '👨‍❤️‍👩', '👩‍❤️‍👨', '👨‍❤️‍👨'] }, 
                    { section: 'Animales', items: ['🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🦁', '🐯', '🐨', '🦝', '🦋', '🐞', '🐜', '🦗', '🕷️', '🕸️', '🦂', '🐍', '🦎', '🐢', '🐸', '🦉', '🦅', '🦜', '🦚', '🦆', '🦑', '🐙','🦞', '🦈', '🐠', '🐟', '🐡', '🦕', '🦖', '🐬', '🐳', '🐋', '🦑', '🦚', '🦜', '🦇', '🦦', '🦈', '🦟', '🦠', '🦐', '🦋', '🦄', '🐉'] }, 
                    { section: 'Viajes y lugares', items: ['🌍', '🌎', '🌏', '🏔️', '⛰️', '🗻', '🌋', '🏜️', '🏝️', '🏖️', '🏕️', '🏠', '🏡', '🏘️', '🏚️', '🏛️', '🏟️', '🏗️', '🏘️', '🏚️', '🕌', '🕍', '🕋', '⛪', '🛕', '🏰', '🏯', '🏬', '🏢', '🏣', '🏤', '🏥', '🏦', '🏪', '🏫', '🏩', '🏨'] }, 
                    { section: 'Objetos', items: ['📱', '📲', '💻', '⌨️', '🖥️', '🖨️', '🖱️', '🖲️', '💽', '💾', '💿', '📀', '📼', '📹', '📺', '📷', '📸', '📽', '🎥', '📞', '☎️', '📟', '📠', '📧', '📨', '📩', '📪', '📫', '📬', '📭', '📮', '📯', '📥', '📤'] }, 
                    { section: 'Simbolos', items: ['❤️', '💔', '💖', '💗', '💙', '💚', '💛', '💜', '🖤', '🤍', '🤎', '💝', '💞', '💟', '❣️', '💕', '💓', '💔', '🧡', '💯'] }, 
                ]; 
                emojis.forEach(function (emojiSection) {
                    // Crear la sección
                    const sectionDiv = document.createElement('div');
                    sectionDiv.classList.add('emoji-section');
                    
                    // Crear el encabezado de la sección
                    const sectionHeader = document.createElement('h3');
                    sectionHeader.textContent = emojiSection.section;
                    sectionDiv.appendChild(sectionHeader);
            
                    // Agregar emojis a la sección
                    emojiSection.items.forEach(function (emoji) {
                        const emojiSpan = document.createElement('span');
                        emojiSpan.classList.add('emoji');
                        emojiSpan.textContent = emoji;
                        sectionDiv.appendChild(emojiSpan);
            
                        emojiSpan.addEventListener('click', function () {
                            messageInput.value += emojiSpan.textContent;
                            emojiPicker.style.display = 'none';
                        });
                    });
            
                    // Añadir la sección al picker
                    emojiPickerBody.appendChild(sectionDiv);
                });
            }
        });