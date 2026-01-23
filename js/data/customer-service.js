/**
 * Customer Service Templates - Müşteri Hizmetleri Şablonları
 * Sektöre göre kategorize edilmiş hazır cevaplar
 */

const CustomerServiceTemplates = {
    // Genel müşteri hizmetleri
    general: {
        name: 'Genel',
        icon: 'fas fa-headset',
        templates: [
            {
                trigger: '/merhaba',
                text: 'Merhaba, {firma_adi} Müşteri Hizmetleri\'ne hoş geldiniz. Size nasıl yardımcı olabilirim?',
                description: 'Karşılama mesajı'
            },
            {
                trigger: '/yardım',
                text: 'Size yardımcı olmaktan memnuniyet duyarım. Lütfen sorununuzu veya isteğinizi detaylı şekilde paylaşır mısınız?',
                description: 'Yardım teklifi'
            },
            {
                trigger: '/bekle',
                text: 'Lütfen bir dakika bekler misiniz? Bilgilerinizi kontrol ediyorum.',
                description: 'Bekleme isteği'
            },
            {
                trigger: '/anladım',
                text: 'Anladım, sorununuzu çözmek için elimden geleni yapacağım.',
                description: 'Anlama onayı'
            },
            {
                trigger: '/başka',
                text: 'Başka bir konuda yardımcı olabilir miyim?',
                description: 'Ek yardım teklifi'
            },
            {
                trigger: '/kapanış',
                text: 'Bizi tercih ettiğiniz için teşekkür ederiz. İyi günler dilerim, görüşmek üzere.',
                description: 'Kapanış mesajı'
            },
            {
                trigger: '/özür',
                text: 'Yaşadığınız bu durumdan dolayı çok üzgünüz. Sorununuzu çözmek için hemen harekete geçiyorum.',
                description: 'Özür mesajı'
            },
            {
                trigger: '/teşekkür',
                text: 'Anlayışınız ve sabrınız için teşekkür ederim.',
                description: 'Teşekkür mesajı'
            }
        ]
    },

    // E-ticaret
    ecommerce: {
        name: 'E-Ticaret',
        icon: 'fas fa-shopping-cart',
        templates: [
            {
                trigger: '/sipariş-sorgula',
                text: 'Siparişinizi sorgulayabilmem için sipariş numaranızı paylaşır mısınız?',
                description: 'Sipariş sorgulama'
            },
            {
                trigger: '/sipariş-durum',
                text: 'Siparişiniz şu anda {durum} aşamasındadır. Tahmini teslimat tarihi: {tarih}.',
                description: 'Sipariş durumu bilgisi'
            },
            {
                trigger: '/kargo',
                text: 'Siparişiniz kargoya verilmiştir. Kargo takip numaranız: {kargo_no}. Kargo firması: {kargo_firma}.',
                description: 'Kargo bilgisi'
            },
            {
                trigger: '/iade',
                text: 'İade talebinizi almak istiyorum. İade etmek istediğiniz ürünün sipariş numarası ve iade nedeni nedir?',
                description: 'İade talebi'
            },
            {
                trigger: '/iade-onay',
                text: 'İade talebiniz onaylanmıştır. Ürünü orijinal ambalajında kargoya vermeniz gerekmektedir. İade kodunuz: {iade_kod}.',
                description: 'İade onayı'
            },
            {
                trigger: '/değişim',
                text: 'Ürün değişimi için sipariş numaranızı ve değiştirmek istediğiniz ürün bilgisini paylaşır mısınız?',
                description: 'Değişim talebi'
            },
            {
                trigger: '/stok',
                text: 'Ürünümüz şu anda {durum}. {ek_bilgi}',
                description: 'Stok durumu'
            },
            {
                trigger: '/fiyat',
                text: 'Ürünün güncel fiyatı {fiyat} TL\'dir. {kampanya_bilgisi}',
                description: 'Fiyat bilgisi'
            },
            {
                trigger: '/kampanya',
                text: 'Şu anda geçerli kampanyalarımız: {kampanya_listesi}. Daha fazla bilgi almak ister misiniz?',
                description: 'Kampanya bilgisi'
            },
            {
                trigger: '/teslimat',
                text: 'Teslimat süresi bulunduğunuz bölgeye göre {sure} iş günüdür. Kargo ücreti: {ucret} TL.',
                description: 'Teslimat bilgisi'
            }
        ]
    },

    // Ödeme ve Finans
    payment: {
        name: 'Ödeme',
        icon: 'fas fa-credit-card',
        templates: [
            {
                trigger: '/ödeme-başarılı',
                text: 'Ödemeniz başarıyla alınmıştır. İşlem numaranız: {islem_no}. Teşekkür ederiz.',
                description: 'Başarılı ödeme'
            },
            {
                trigger: '/ödeme-hata',
                text: 'Ödeme işleminizde bir sorun oluştu. Lütfen kart bilgilerinizi kontrol ediniz veya farklı bir ödeme yöntemi deneyiniz.',
                description: 'Ödeme hatası'
            },
            {
                trigger: '/fatura',
                text: 'Faturanız e-posta adresinize gönderilmiştir. Fatura tutarı: {tutar} TL. Son ödeme tarihi: {tarih}.',
                description: 'Fatura bilgisi'
            },
            {
                trigger: '/taksit',
                text: 'Taksit seçeneklerimiz: {taksit_listesi}. Hangi taksit seçeneğini tercih edersiniz?',
                description: 'Taksit seçenekleri'
            },
            {
                trigger: '/iade-ödeme',
                text: 'İade tutarınız {tutar} TL, {sure} iş günü içinde kartınıza/hesabınıza yansıyacaktır.',
                description: 'İade ödemesi'
            },
            {
                trigger: '/ödeme-yöntem',
                text: 'Kabul ettiğimiz ödeme yöntemleri: Kredi Kartı, Banka Kartı, Havale/EFT, Kapıda Ödeme.',
                description: 'Ödeme yöntemleri'
            }
        ]
    },

    // Teknik Destek
    technical: {
        name: 'Teknik Destek',
        icon: 'fas fa-tools',
        templates: [
            {
                trigger: '/teknik-bilgi',
                text: 'Sorununuzu daha iyi anlayabilmem için şu bilgileri paylaşır mısınız: Cihaz/uygulama adı, işletim sistemi, hata mesajı?',
                description: 'Teknik bilgi isteme'
            },
            {
                trigger: '/yeniden-başlat',
                text: 'Lütfen cihazınızı/uygulamanızı yeniden başlatmayı deneyin. Bu işlem çoğu sorunu çözer.',
                description: 'Yeniden başlatma önerisi'
            },
            {
                trigger: '/güncelleme',
                text: 'Lütfen uygulamanızın/sisteminizin güncel olduğundan emin olun. En son sürümü kullanmanızı öneririz.',
                description: 'Güncelleme önerisi'
            },
            {
                trigger: '/cache-temizle',
                text: 'Önbellek temizleme işlemi yapmanızı öneririm. Ayarlar > Uygulama > Önbelleği Temizle yolunu izleyebilirsiniz.',
                description: 'Önbellek temizleme'
            },
            {
                trigger: '/şifre-sıfırla',
                text: 'Şifrenizi sıfırlamak için "Şifremi Unuttum" seçeneğini kullanabilirsiniz. E-posta adresinize sıfırlama linki gönderilecektir.',
                description: 'Şifre sıfırlama'
            },
            {
                trigger: '/uzman',
                text: 'Sorununuzu teknik ekibimize iletiyorum. Size 24 saat içinde dönüş yapılacaktır.',
                description: 'Uzmana yönlendirme'
            }
        ]
    },

    // Şikayet Yönetimi
    complaints: {
        name: 'Şikayet',
        icon: 'fas fa-exclamation-triangle',
        templates: [
            {
                trigger: '/şikayet-al',
                text: 'Şikayetinizi aldım ve üzüntüyle karşıladım. Bu durumun düzeltilmesi için gereken adımları atacağım.',
                description: 'Şikayet kabul'
            },
            {
                trigger: '/anlıyorum',
                text: 'Yaşadığınız durumu tamamen anlıyorum. Bu kesinlikle kabul edilemez ve hemen çözüme kavuşturacağım.',
                description: 'Empati gösterme'
            },
            {
                trigger: '/inceleme',
                text: 'Durumu incelemeye aldım. En geç 48 saat içinde size detaylı bilgi vereceğiz.',
                description: 'İnceleme bildirimi'
            },
            {
                trigger: '/çözüm',
                text: 'Sorununuzu çözmek için şu adımları atıyoruz: {adimlar}. Bu süreçte sizi bilgilendireceğiz.',
                description: 'Çözüm planı'
            },
            {
                trigger: '/tazminat',
                text: 'Yaşadığınız olumsuzluk için size {tazminat} sunmak istiyoruz. Bu öneriyi kabul eder misiniz?',
                description: 'Tazminat teklifi'
            }
        ]
    },

    // Randevu ve Rezervasyon
    appointment: {
        name: 'Randevu',
        icon: 'fas fa-calendar-alt',
        templates: [
            {
                trigger: '/randevu-al',
                text: 'Randevu almak için hangi tarih ve saat aralığını tercih edersiniz?',
                description: 'Randevu isteği'
            },
            {
                trigger: '/randevu-onay',
                text: 'Randevunuz oluşturulmuştur. Tarih: {tarih}, Saat: {saat}. Randevu kodunuz: {kod}.',
                description: 'Randevu onayı'
            },
            {
                trigger: '/randevu-iptal',
                text: 'Randevunuz iptal edilmiştir. Yeni bir randevu oluşturmak ister misiniz?',
                description: 'Randevu iptal'
            },
            {
                trigger: '/randevu-güncelle',
                text: 'Randevunuzu güncellemek için yeni tarih ve saat bilgisini paylaşır mısınız?',
                description: 'Randevu güncelleme'
            },
            {
                trigger: '/müsaitlik',
                text: 'Müsait randevu saatlerimiz: {saatler}. Hangi saati tercih edersiniz?',
                description: 'Müsaitlik bilgisi'
            }
        ]
    },

    // Hesap İşlemleri
    account: {
        name: 'Hesap',
        icon: 'fas fa-user-cog',
        templates: [
            {
                trigger: '/hesap-doğrula',
                text: 'Hesabınızı doğrulamak için kayıtlı telefon numaranıza/e-posta adresinize gönderilen kodu paylaşır mısınız?',
                description: 'Hesap doğrulama'
            },
            {
                trigger: '/hesap-güncelle',
                text: 'Hesap bilgilerinizi güncellemek için hangi bilginizi değiştirmek istiyorsunuz?',
                description: 'Hesap güncelleme'
            },
            {
                trigger: '/üyelik',
                text: 'Üyelik planlarımız: {planlar}. Size en uygun planı önerebilirim, tercihleriniz nelerdir?',
                description: 'Üyelik bilgisi'
            },
            {
                trigger: '/iptal-üyelik',
                text: 'Üyelik iptal talebinizi aldım. İptal sebebini öğrenebilir miyim? Size daha iyi hizmet vermek istiyoruz.',
                description: 'Üyelik iptal'
            }
        ]
    }
};

// Şablon arama fonksiyonu
function searchTemplates(query) {
    const results = [];
    const searchTerm = query.toLowerCase().trim();

    Object.entries(CustomerServiceTemplates).forEach(([categoryKey, category]) => {
        category.templates.forEach(template => {
            // Trigger veya description içinde ara
            if (template.trigger.toLowerCase().includes(searchTerm) ||
                template.description.toLowerCase().includes(searchTerm) ||
                template.text.toLowerCase().includes(searchTerm)) {
                results.push({
                    ...template,
                    category: category.name,
                    categoryIcon: category.icon
                });
            }
        });
    });

    return results;
}

// Trigger ile şablon bul
function findTemplateByTrigger(trigger) {
    const normalizedTrigger = trigger.toLowerCase().trim();

    for (const category of Object.values(CustomerServiceTemplates)) {
        for (const template of category.templates) {
            if (template.trigger.toLowerCase() === normalizedTrigger) {
                return {
                    ...template,
                    category: category.name,
                    categoryIcon: category.icon
                };
            }
        }
    }

    return null;
}

// Global export
if (typeof window !== 'undefined') {
    window.CustomerServiceTemplates = CustomerServiceTemplates;
    window.searchTemplates = searchTemplates;
    window.findTemplateByTrigger = findTemplateByTrigger;
}
