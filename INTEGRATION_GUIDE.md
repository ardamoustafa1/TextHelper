# TextHelper Chat AI Entegrasyon Kılavuzu

Bu kılavuz, TextHelper sistemini kendi Chat AI projenize nasıl entegre edeceğinizi gösterir.

## 🎯 Hızlı Başlangıç

### 1. Dosyaları Projenize Kopyalayın

TextHelper klasöründeki tüm dosyaları projenize kopyalayın:

```
YourProject/
├── js/
│   ├── autocomplete/          # TextHelper modülleri
│   ├── ui/                    # UI bileşenleri
│   └── data/                  # Sözlük ve veriler
├── css/
│   └── styles.css             # TextHelper stilleri (isteğe bağlı)
└── your-chat-ai.html          # Chat AI sayfanız
```

### 2. HTML'e Script'leri Ekleyin

Chat AI sayfanızın `<head>` veya `</body>` öncesine ekleyin:

```html
<!-- TextHelper Scripts (Sırayla!) -->
<script src="js/data/turkish-dictionary.js"></script>
<script src="js/data/common-phrases.js"></script>
<script src="js/data/customer-service.js"></script>
<script src="js/autocomplete/NGramModel.js"></script>
<script src="js/autocomplete/ContextAnalyzer.js"></script>
<script src="js/autocomplete/TemplateManager.js"></script>
<script src="js/autocomplete/HistoryManager.js"></script>
<script src="js/autocomplete/SpellChecker.js"></script>
<script src="js/autocomplete/PredictionService.js"></script>
<script src="js/autocomplete/BackgroundService.js"></script>
<script src="js/autocomplete/AutocompleteEngine.js"></script>
<script src="js/ui/SuggestionDropdown.js"></script>
<script src="js/ui/KeyboardHandler.js"></script>
```

### 3. Basit Entegrasyon (En Kolay Yol)

```javascript
// Chat AI sayfanızda
class YourChatAI {
    constructor() {
        this.messageInput = document.getElementById('yourMessageInput');
        this.autocompleteEngine = null;
        this.initAutocomplete();
    }
    
    initAutocomplete() {
        // Autocomplete Engine oluştur
        this.autocompleteEngine = new AutocompleteEngine({
            minInputLength: 1,      // Tek harf için de öneriler
            maxSuggestions: 7,
            debounceMs: 30,
            autoLearn: true
        });
        
        // Input'a bağla
        this.autocompleteEngine.attach(this.messageInput);
        
        // Öneri güncellemelerini dinle
        this.autocompleteEngine.onSuggestionsUpdate = (suggestions, selectedIndex) => {
            this.showSuggestions(suggestions, selectedIndex);
        };
        
        // Öneri seçimini dinle
        this.autocompleteEngine.onSuggestionSelect = (suggestion) => {
            console.log('Seçilen öneri:', suggestion);
        };
    }
    
    showSuggestions(suggestions, selectedIndex) {
        // Kendi UI'ınızda gösterin
        // Örnek: Dropdown, tooltip, vb.
        const dropdown = document.getElementById('suggestionsDropdown');
        if (suggestions.length > 0) {
            dropdown.innerHTML = suggestions.map((s, i) => `
                <div class="suggestion-item ${i === selectedIndex ? 'active' : ''}" 
                     onclick="selectSuggestion(${i})">
                    <i class="${s.icon}"></i>
                    <span>${s.text}</span>
                    ${s.description ? `<small>${s.description}</small>` : ''}
                </div>
            `).join('');
            dropdown.style.display = 'block';
        } else {
            dropdown.style.display = 'none';
        }
    }
    
    selectSuggestion(index) {
        this.autocompleteEngine.selectSuggestion(index);
    }
    
    // Mesaj gönderildiğinde
    sendMessage() {
        const text = this.messageInput.value.trim();
        if (!text) return;
        
        // Chat AI'ya gönder
        this.sendToAI(text);
        
        // Autocomplete'e bildir (öğrenme için)
        if (this.autocompleteEngine) {
            this.autocompleteEngine.onMessageSent(text);
        }
        
        // Input'u temizle
        this.messageInput.value = '';
    }
}

// Kullanım
const chatAI = new YourChatAI();
```

## 🔧 Gelişmiş Entegrasyon

### React ile Entegrasyon

```jsx
import { useEffect, useRef, useState } from 'react';

function ChatInput() {
    const inputRef = useRef(null);
    const [suggestions, setSuggestions] = useState([]);
    const [selectedIndex, setSelectedIndex] = useState(0);
    const engineRef = useRef(null);
    
    useEffect(() => {
        // Script'lerin yüklendiğinden emin olun
        if (typeof AutocompleteEngine === 'undefined') {
            console.error('AutocompleteEngine yüklenmedi!');
            return;
        }
        
        // Engine oluştur
        engineRef.current = new AutocompleteEngine({
            minInputLength: 1,
            maxSuggestions: 7,
            autoLearn: true
        });
        
        // Input'a bağla
        if (inputRef.current) {
            engineRef.current.attach(inputRef.current);
            
            // Öneri güncellemelerini dinle
            engineRef.current.onSuggestionsUpdate = (sugs, idx) => {
                setSuggestions(sugs);
                setSelectedIndex(idx);
            };
        }
        
        // Cleanup
        return () => {
            if (engineRef.current) {
                engineRef.current.detach();
            }
        };
    }, []);
    
    const handleSend = () => {
        const text = inputRef.current?.value.trim();
        if (!text) return;
        
        // Mesajı gönder
        onSendMessage(text);
        
        // Öğrenme
        if (engineRef.current) {
            engineRef.current.onMessageSent(text);
        }
        
        inputRef.current.value = '';
    };
    
    return (
        <div className="chat-input-container">
            <input 
                ref={inputRef} 
                type="text" 
                placeholder="Mesajınızı yazın..."
            />
            
            {/* Öneriler */}
            {suggestions.length > 0 && (
                <div className="suggestions-dropdown">
                    {suggestions.map((sug, idx) => (
                        <div 
                            key={idx}
                            className={`suggestion-item ${idx === selectedIndex ? 'active' : ''}`}
                            onClick={() => engineRef.current?.selectSuggestion(idx)}
                        >
                            <i className={sug.icon}></i>
                            <span>{sug.text}</span>
                        </div>
                    ))}
                </div>
            )}
            
            <button onClick={handleSend}>Gönder</button>
        </div>
    );
}
```

### Vue.js ile Entegrasyon

```vue
<template>
    <div class="chat-input">
        <textarea 
            ref="messageInput"
            v-model="message"
            @input="handleInput"
            placeholder="Mesajınızı yazın..."
        />
        
        <!-- Öneriler -->
        <div v-if="suggestions.length > 0" class="suggestions">
            <div 
                v-for="(sug, index) in suggestions"
                :key="index"
                :class="['suggestion-item', { active: index === selectedIndex }]"
                @click="selectSuggestion(index)"
            >
                <i :class="sug.icon"></i>
                <span>{{ sug.text }}</span>
            </div>
        </div>
        
        <button @click="sendMessage">Gönder</button>
    </div>
</template>

<script>
export default {
    data() {
        return {
            message: '',
            suggestions: [],
            selectedIndex: 0,
            autocompleteEngine: null
        };
    },
    mounted() {
        // Autocomplete Engine'i başlat
        if (typeof AutocompleteEngine !== 'undefined') {
            this.autocompleteEngine = new AutocompleteEngine({
                minInputLength: 1,
                maxSuggestions: 7,
                autoLearn: true
            });
            
            this.autocompleteEngine.attach(this.$refs.messageInput);
            
            this.autocompleteEngine.onSuggestionsUpdate = (sugs, idx) => {
                this.suggestions = sugs;
                this.selectedIndex = idx;
            };
        }
    },
    methods: {
        handleInput() {
            // Input değiştiğinde otomatik olarak öneriler güncellenir
        },
        selectSuggestion(index) {
            if (this.autocompleteEngine) {
                this.autocompleteEngine.selectSuggestion(index);
            }
        },
        sendMessage() {
            if (!this.message.trim()) return;
            
            // Mesajı gönder
            this.$emit('send', this.message);
            
            // Öğrenme
            if (this.autocompleteEngine) {
                this.autocompleteEngine.onMessageSent(this.message);
            }
            
            this.message = '';
        }
    },
    beforeUnmount() {
        if (this.autocompleteEngine) {
            this.autocompleteEngine.detach();
        }
    }
};
</script>
```

### Vanilla JavaScript ile Entegrasyon

```javascript
// Chat AI sınıfınızda
class ChatAI {
    constructor() {
        this.inputElement = document.querySelector('#chatInput');
        this.autocompleteEngine = null;
        this.init();
    }
    
    init() {
        // Autocomplete Engine'i başlat
        this.autocompleteEngine = new AutocompleteEngine({
            minInputLength: 1,
            maxSuggestions: 7,
            debounceMs: 30,
            autoLearn: true
        });
        
        // Input'a bağla
        this.autocompleteEngine.attach(this.inputElement);
        
        // Öneri güncellemelerini dinle
        this.autocompleteEngine.onSuggestionsUpdate = (suggestions, selectedIndex) => {
            this.renderSuggestions(suggestions, selectedIndex);
        };
        
        // Klavye olayları
        this.inputElement.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
    }
    
    renderSuggestions(suggestions, selectedIndex) {
        const container = document.querySelector('#suggestionsContainer');
        if (!container) return;
        
        if (suggestions.length === 0) {
            container.innerHTML = '';
            container.style.display = 'none';
            return;
        }
        
        container.innerHTML = suggestions.map((sug, idx) => `
            <div class="suggestion-item ${idx === selectedIndex ? 'active' : ''}" 
                 data-index="${idx}">
                <i class="${sug.icon || 'fas fa-comment'}"></i>
                <span class="suggestion-text">${sug.text}</span>
                ${sug.description ? `<span class="suggestion-desc">${sug.description}</span>` : ''}
            </div>
        `).join('');
        
        container.style.display = 'block';
        
        // Click event'leri
        container.querySelectorAll('.suggestion-item').forEach((item, idx) => {
            item.addEventListener('click', () => {
                this.autocompleteEngine.selectSuggestion(idx);
            });
        });
    }
    
    sendMessage() {
        const text = this.inputElement.value.trim();
        if (!text) return;
        
        // Chat AI'ya gönder
        this.sendToAI(text);
        
        // Öğrenme
        this.autocompleteEngine.onMessageSent(text);
        
        // Temizle
        this.inputElement.value = '';
        document.querySelector('#suggestionsContainer').style.display = 'none';
    }
    
    sendToAI(message) {
        // Kendi Chat AI entegrasyonunuz
        // Örnek: API çağrısı, WebSocket, vb.
        console.log('Sending to AI:', message);
    }
}

// Kullanım
const chatAI = new ChatAI();
```

## 🎨 CSS Stilleri

Kendi stillerinizi ekleyebilirsiniz veya TextHelper'ın stillerini kullanabilirsiniz:

```css
/* Öneri dropdown */
.suggestions-container {
    position: absolute;
    bottom: 100%;
    left: 0;
    right: 0;
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    max-height: 300px;
    overflow-y: auto;
    z-index: 1000;
    margin-bottom: 8px;
}

.suggestion-item {
    padding: 12px 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 12px;
    border-bottom: 1px solid #f0f0f0;
    transition: background 0.2s;
}

.suggestion-item:hover,
.suggestion-item.active {
    background: #f5f5f5;
}

.suggestion-item i {
    color: #666;
    width: 20px;
}

.suggestion-text {
    flex: 1;
    font-weight: 500;
}

.suggestion-desc {
    font-size: 0.85em;
    color: #999;
}
```

## 🔌 API Referansı

### AutocompleteEngine Metodları

```javascript
// Engine oluştur
const engine = new AutocompleteEngine(options);

// Input'a bağla
engine.attach(inputElement);

// Input'tan ayır
engine.detach();

// Öneri seç
engine.selectSuggestion(index);

// Mesaj gönderildi (öğrenme için)
engine.onMessageSent(message);

// Öneri güncellemelerini dinle
engine.onSuggestionsUpdate = (suggestions, selectedIndex) => {
    // suggestions: Array<{text, icon, description, score, ...}>
    // selectedIndex: number
};

// Öneri seçimini dinle
engine.onSuggestionSelect = (suggestion) => {
    // suggestion: {text, icon, description, ...}
};

// Etkinleştir/Devre dışı bırak
engine.setEnabled(true);

// Konfigürasyon güncelle
engine.updateConfig({ maxSuggestions: 10 });

// İstatistikler
const stats = engine.getStats();
```

### BackgroundService Metodları

```javascript
const service = new BackgroundService();

// Tahmin isteği
service.predict(input, (suggestions) => {
    console.log(suggestions);
});

// Öğrenme
service.learn(message);

// Toplu öğrenme
service.learnBatch([message1, message2, message3]);

// Önbelleği temizle
service.clearCache();

// İstatistikler
const stats = service.getStats();
```

## 📝 Önemli Notlar

1. **Script Sırası**: Script'leri mutlaka belirtilen sırayla yükleyin
2. **Input Element**: Textarea veya input elementi olabilir
3. **Öğrenme**: Mesaj gönderildiğinde `onMessageSent()` çağrılmalı
4. **Performans**: BackgroundService kullanırsanız daha iyi performans alırsınız
5. **Özelleştirme**: Tüm ayarlar konfigürasyon objesi ile yapılabilir

## 🐛 Sorun Giderme

### Öneriler çıkmıyor
- Script'lerin yüklendiğinden emin olun
- Console'da hata var mı kontrol edin
- `minInputLength` ayarını kontrol edin

### Yazım düzeltme çalışmıyor
- SpellChecker script'inin yüklendiğinden emin olun
- Sözlüğün yüklendiğini kontrol edin

### Performans sorunları
- BackgroundService kullanın
- Debounce süresini artırın
- Önbellek boyutunu kontrol edin

## 💡 İpuçları

1. **Kendi UI'ınızı kullanın**: TextHelper sadece önerileri sağlar, UI'ı siz tasarlayın
2. **Öğrenmeyi aktif tutun**: `autoLearn: true` ile sistem sürekli gelişir
3. **Özelleştirin**: Kendi şablonlarınızı ve kelimelerinizi ekleyin
4. **Performans**: Büyük projelerde BackgroundService kullanın

## 📞 Destek

Sorularınız için lütfen iletişime geçin.

---

**TextHelper** - Chat AI projeleriniz için profesyonel otomatik tamamlama sistemi
