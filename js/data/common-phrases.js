/**
 * Common Phrases - Yaygın Türkçe İfadeler ve Kalıplar
 * Müşteri hizmetleri ve günlük konuşma için
 */

const CommonPhrases = {
    // Selamlama ifadeleri
    greetings: {
        formal: [
            'Merhaba, size nasıl yardımcı olabilirim?',
            'İyi günler, hoş geldiniz.',
            'Günaydın, bugün size nasıl yardımcı olabilirim?',
            'İyi akşamlar, hoş geldiniz.',
            'Değerli müşterimiz, merhaba.',
            'Sayın müşterimiz, hoş geldiniz.',
            'Müşteri Hizmetleri\'ne hoş geldiniz.'
        ],
        informal: [
            'Merhaba!',
            'Selam, nasılsın?',
            'Hoş geldin!',
            'İyi günler!',
            'Merhabalar!'
        ],
        followUp: [
            'Size nasıl yardımcı olabilirim?',
            'Bugün size nasıl destek olabilirim?',
            'Ne konuda yardımcı olabilirim?',
            'Sizi dinliyorum.',
            'Nasıl yardımcı olabilirim?'
        ]
    },

    // Teşekkür ifadeleri
    thanks: {
        giving: [
            'Teşekkür ederim.',
            'Çok teşekkür ederim.',
            'Teşekkürler.',
            'Sağ olun.',
            'Anlayışınız için teşekkür ederiz.',
            'Bizi tercih ettiğiniz için teşekkürler.',
            'Değerli görüşleriniz için teşekkür ederiz.',
            'Sabırınız için teşekkür ederim.',
            'Zaman ayırdığınız için teşekkürler.'
        ],
        receiving: [
            'Rica ederim.',
            'Bir şey değil.',
            'Ne demek, her zaman.',
            'Yardımcı olabildiysem ne mutlu.',
            'Memnuniyetle.',
            'Her zaman yardımcı olmaktan memnuniyet duyarız.'
        ]
    },

    // Özür ifadeleri
    apologies: {
        general: [
            'Özür dilerim.',
            'Çok özür dilerim.',
            'Kusura bakmayın.',
            'Affedersiniz.',
            'Pardon.'
        ],
        customerService: [
            'Bu durumdan dolayı özür dileriz.',
            'Yaşadığınız sorun için çok üzgünüz.',
            'Verdiğimiz rahatsızlıktan dolayı özür dileriz.',
            'Bu olumsuz deneyim için özür dileriz.',
            'Beklentilerinizi karşılayamadığımız için üzgünüz.',
            'Gecikme için özür dileriz.',
            'Size yaşattığımız bu durumdan dolayı çok üzgünüz.'
        ]
    },

    // Yardım teklifi
    helpOffers: [
        'Size yardımcı olmaktan memnuniyet duyarım.',
        'Bu konuda size destek olmak isteriz.',
        'Size yardımcı olabilmemiz için lütfen detay paylaşır mısınız?',
        'Size en iyi şekilde yardımcı olmak istiyoruz.',
        'Bu sorunu çözmek için elimizden geleni yapacağız.',
        'Sizin için ne yapabilirim?',
        'Bu konuda size nasıl destek olabilirim?'
    ],

    // Bekleme istekleri
    waitRequests: [
        'Bir dakika bekler misiniz lütfen?',
        'Lütfen bir an bekleyin.',
        'Kontrol ediyorum, bir dakika.',
        'Sizin için bakıyorum, lütfen bekleyin.',
        'Bilgilerinizi kontrol ediyorum.',
        'Bir saniye, hemen bakıyorum.',
        'Sistemden kontrol ediyorum, lütfen bekleyiniz.'
    ],

    // Bilgi isteme
    infoRequests: [
        'Bu konuyla ilgili daha fazla bilgi verebilir misiniz?',
        'Sipariş numaranızı paylaşır mısınız?',
        'Müşteri numaranızı öğrenebilir miyim?',
        'Telefon numaranızı doğrulayabilir miyiz?',
        'E-posta adresinizi paylaşır mısınız?',
        'Yaşadığınız sorunu detaylı anlatır mısınız?',
        'Hangi ürün/hizmet hakkında bilgi almak istiyorsunuz?',
        'TC Kimlik numaranızın son 4 hanesini öğrenebilir miyim?'
    ],

    // Onay ve doğrulama
    confirmations: [
        'Anladım, teşekkür ederim.',
        'Bilgilerinizi aldım.',
        'Talebiniz alınmıştır.',
        'İşleminiz tamamlanmıştır.',
        'Kaydınız yapılmıştır.',
        'Bilgileriniz güncellenmiştir.',
        'Talebiniz işleme alınmıştır.',
        'Evet, doğru anladım.',
        'Onaylanmıştır.'
    ],

    // Bilgi verme
    infoProviding: [
        'Size bilgi vermek isterim.',
        'Bu konuda şunu söyleyebilirim:',
        'Bilginize sunmak isterim ki...',
        'Size şu bilgiyi paylaşmak istiyorum:',
        'Bu durumda yapmanız gereken...',
        'İşlem süreci şu şekildedir:',
        'Bilgilerinize göre...'
    ],

    // Çözüm önerileri
    solutions: [
        'Bu sorunu çözmek için...',
        'Size şu çözümü önerebilirim:',
        'Bu durumda yapabileceğiniz...',
        'Sorununuzu çözmek için şu adımları izleyebilirsiniz:',
        'En hızlı çözüm için...',
        'Size yardımcı olabilecek bir önerim var:'
    ],

    // İletişim devamı
    followUp: [
        'Başka bir konuda yardımcı olabilir miyim?',
        'Başka sorunuz var mı?',
        'Size başka nasıl yardımcı olabilirim?',
        'Eklemek istediğiniz bir şey var mı?',
        'Başka herhangi bir konuda destek olabilir miyim?'
    ],

    // Kapanış
    closings: {
        formal: [
            'İyi günler dilerim.',
            'İyi günler, görüşmek üzere.',
            'Güle güle, iyi günler.',
            'Bizi tercih ettiğiniz için teşekkürler, iyi günler.',
            'Görüşmek üzere, iyi günler dilerim.',
            'Sağlıklı günler dilerim.',
            'Saygılarımla.',
            'En iyi dileklerimle.'
        ],
        informal: [
            'Görüşürüz!',
            'Kendine iyi bak!',
            'Hoşça kal!',
            'Güle güle!'
        ],
        customerService: [
            'Bizi tercih ettiğiniz için teşekkür ederiz.',
            'Müşterimiz olduğunuz için teşekkürler.',
            'Size hizmet vermekten memnuniyet duyduk.',
            'Tekrar görüşmek üzere.',
            'Her zaman hizmetinizdeyiz.',
            'Başka bir ihtiyacınız olursa bize ulaşın.'
        ]
    },

    // Olumlu ifadeler
    positive: [
        'Harika!',
        'Mükemmel!',
        'Çok güzel!',
        'Süper!',
        'Tebrikler!',
        'Ne güzel!',
        'Sevindim!',
        'Bu harika bir haber!'
    ],

    // Olumsuz durumlar
    negative: [
        'Maalesef...',
        'Üzgünüm ama...',
        'Ne yazık ki...',
        'Şu an için mümkün değil.',
        'Bu konuda elimiz kolumuz bağlı.',
        'Maalesef bu mümkün olmayacak.'
    ],

    // Açıklama ifadeleri
    explanations: [
        'Şöyle açıklayayım:',
        'Daha detaylı anlatayım:',
        'Size şunu söyleyebilirim:',
        'Kısaca açıklamak gerekirse:',
        'Özetlemek gerekirse:'
    ],

    // Zaman ifadeleri
    timeExpressions: [
        'En kısa sürede',
        'Hemen',
        'Birkaç dakika içinde',
        'Bugün içinde',
        '24 saat içinde',
        '1-3 iş günü içinde',
        'Bu hafta içinde',
        'En geç yarın'
    ],

    // İletişim bilgisi
    contactInfo: [
        'Bize 444 numaralı hattımızdan ulaşabilirsiniz.',
        'Destek e-posta adresimiz: destek@sirket.com',
        'Web sitemiz üzerinden de bize ulaşabilirsiniz.',
        'WhatsApp hattımızdan 7/24 destek alabilirsiniz.',
        'Mobil uygulamamız üzerinden de iletişime geçebilirsiniz.'
    ]
};

// Global export
if (typeof window !== 'undefined') {
    window.CommonPhrases = CommonPhrases;
}
