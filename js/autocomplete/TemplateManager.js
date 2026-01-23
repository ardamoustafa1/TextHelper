/**
 * Template Manager - Şablon Yönetici
 * Hızlı şablonları ve kısayolları yönetir
 */

class TemplateManager {
    constructor() {
        // Şablon kategorileri
        this.categories = {};

        // Trigger eşleştirmeleri
        this.triggerMap = new Map();

        // Değişken kalıpları
        this.variablePattern = /\{([^}]+)\}/g;

        // Başlangıç şablonlarını yükle
        this._initializeTemplates();
    }

    /**
     * Şablonları başlat
     */
    _initializeTemplates() {
        // CustomerServiceTemplates yüklü mü kontrol et
        if (typeof CustomerServiceTemplates !== 'undefined') {
            this.categories = { ...CustomerServiceTemplates };
            this._buildTriggerMap();
            console.log(`TemplateManager initialized with ${this.triggerMap.size} templates`);
        } else {
            console.warn('CustomerServiceTemplates not loaded, TemplateManager will start empty');
        }
    }

    /**
     * Trigger haritasını oluştur
     */
    _buildTriggerMap() {
        this.triggerMap.clear();

        Object.entries(this.categories).forEach(([categoryKey, category]) => {
            if (!category.templates) return;

            category.templates.forEach(template => {
                this.triggerMap.set(template.trigger.toLowerCase(), {
                    ...template,
                    category: category.name,
                    categoryKey,
                    categoryIcon: category.icon
                });
            });
        });
    }

    /**
     * Trigger ile şablon bul
     * @param {string} trigger - Trigger metni (örn: /merhaba)
     * @returns {Object|null} - Bulunan şablon veya null
     */
    getByTrigger(trigger) {
        return this.triggerMap.get(trigger.toLowerCase()) || null;
    }

    /**
     * Prefix ile şablonları ara
     * @param {string} prefix - Arama metni
     * @returns {Array} - Eşleşen şablonlar
     */
    searchByPrefix(prefix) {
        if (!prefix) return [];

        const normalizedPrefix = prefix.toLowerCase();
        const results = [];

        this.triggerMap.forEach((template, trigger) => {
            if (trigger.includes(normalizedPrefix) ||
                template.description.toLowerCase().includes(normalizedPrefix) ||
                template.text.toLowerCase().includes(normalizedPrefix)) {
                results.push({
                    ...template,
                    matchType: trigger.startsWith(normalizedPrefix) ? 'trigger' : 'content',
                    matchScore: trigger.startsWith(normalizedPrefix) ? 10 : 5
                });
            }
        });

        return results.sort((a, b) => b.matchScore - a.matchScore);
    }

    /**
     * / ile başlayan komutları ara
     * @param {string} input - Kullanıcı girdisi
     * @returns {Array} - Eşleşen şablonlar
     */
    searchCommands(input) {
        if (!input.startsWith('/')) return [];

        const command = input.toLowerCase();
        const results = [];

        this.triggerMap.forEach((template, trigger) => {
            if (trigger.startsWith(command)) {
                results.push({
                    ...template,
                    matchScore: command.length / trigger.length * 10
                });
            }
        });

        return results.sort((a, b) => b.matchScore - a.matchScore);
    }

    /**
     * Kategoriye göre şablonları al
     * @param {string} categoryKey - Kategori anahtarı
     * @returns {Array} - Şablonlar
     */
    getByCategory(categoryKey) {
        const category = this.categories[categoryKey];
        if (!category) return [];

        return category.templates.map(template => ({
            ...template,
            category: category.name,
            categoryIcon: category.icon
        }));
    }

    /**
     * Tüm kategorileri al
     * @returns {Array} - Kategoriler
     */
    getAllCategories() {
        return Object.entries(this.categories).map(([key, category]) => ({
            key,
            name: category.name,
            icon: category.icon,
            templateCount: category.templates?.length || 0
        }));
    }

    /**
     * Şablon metnini değişkenlerle doldur
     * @param {string} text - Şablon metni
     * @param {Object} variables - Değişken değerleri
     * @returns {string} - Doldurulmuş metin
     */
    fillVariables(text, variables = {}) {
        return text.replace(this.variablePattern, (match, varName) => {
            return variables[varName] || match;
        });
    }

    /**
     * Şablondaki değişkenleri çıkar
     * @param {string} text - Şablon metni
     * @returns {Array} - Değişken isimleri
     */
    extractVariables(text) {
        const variables = [];
        let match;

        while ((match = this.variablePattern.exec(text)) !== null) {
            if (!variables.includes(match[1])) {
                variables.push(match[1]);
            }
        }

        // Pattern'ı sıfırla
        this.variablePattern.lastIndex = 0;

        return variables;
    }

    /**
     * Yeni şablon ekle
     * @param {string} categoryKey - Kategori anahtarı
     * @param {Object} template - Şablon objesi
     */
    addTemplate(categoryKey, template) {
        if (!this.categories[categoryKey]) {
            this.categories[categoryKey] = {
                name: categoryKey,
                icon: 'fas fa-file-alt',
                templates: []
            };
        }

        this.categories[categoryKey].templates.push(template);
        this._buildTriggerMap();
    }

    /**
     * Şablon sil
     * @param {string} trigger - Şablon trigger'ı
     */
    removeTemplate(trigger) {
        const normalizedTrigger = trigger.toLowerCase();

        Object.values(this.categories).forEach(category => {
            if (!category.templates) return;

            const index = category.templates.findIndex(t =>
                t.trigger.toLowerCase() === normalizedTrigger
            );

            if (index !== -1) {
                category.templates.splice(index, 1);
            }
        });

        this._buildTriggerMap();
    }

    /**
     * Özel şablonları kaydet (localStorage)
     */
    saveCustomTemplates() {
        const customTemplates = this.categories.custom?.templates || [];
        localStorage.setItem('texthelper_custom_templates', JSON.stringify(customTemplates));
    }

    /**
     * Özel şablonları yükle
     */
    loadCustomTemplates() {
        try {
            const saved = localStorage.getItem('texthelper_custom_templates');
            if (saved) {
                const customTemplates = JSON.parse(saved);
                this.categories.custom = {
                    name: 'Özel',
                    icon: 'fas fa-star',
                    templates: customTemplates
                };
                this._buildTriggerMap();
            }
        } catch (e) {
            console.error('Failed to load custom templates:', e);
        }
    }

    /**
     * Bağlama göre şablon önerileri
     * @param {Object} context - Bağlam analizi sonucu
     * @returns {Array} - Önerilen şablonlar
     */
    suggestByContext(context) {
        if (!context) return [];

        const suggestions = [];

        // Bağlam türüne göre uygun kategorileri seç
        const categoryMappings = {
            'greeting': ['general'],
            'farewell': ['general'],
            'thanks': ['general'],
            'complaint': ['complaints', 'general'],
            'question': ['technical', 'general', 'ecommerce'],
            'request': ['ecommerce', 'payment', 'account']
        };

        const relevantCategories = categoryMappings[context.type] || ['general'];

        relevantCategories.forEach(catKey => {
            const templates = this.getByCategory(catKey);

            templates.forEach(template => {
                // Bağlama göre skorla
                let score = 1;

                // Anahtar kelime eşleşmesi
                context.keywords?.forEach(keyword => {
                    if (template.text.toLowerCase().includes(keyword) ||
                        template.description.toLowerCase().includes(keyword)) {
                        score += 2;
                    }
                });

                // Duygu eşleşmesi
                if (context.sentiment === 'negative' &&
                    (template.trigger.includes('özür') || template.trigger.includes('şikayet'))) {
                    score += 3;
                }

                suggestions.push({
                    ...template,
                    contextScore: score
                });
            });
        });

        return suggestions
            .sort((a, b) => b.contextScore - a.contextScore)
            .slice(0, 5);
    }

    /**
     * İstatistikler
     */
    getStats() {
        let totalTemplates = 0;
        const categoryStats = {};

        Object.entries(this.categories).forEach(([key, category]) => {
            const count = category.templates?.length || 0;
            totalTemplates += count;
            categoryStats[key] = count;
        });

        return {
            totalTemplates,
            totalCategories: Object.keys(this.categories).length,
            categoryStats
        };
    }
}

// Global export
if (typeof window !== 'undefined') {
    window.TemplateManager = TemplateManager;
}
