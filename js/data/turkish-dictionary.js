/**
 * Turkish Dictionary - Sık Kullanılan Türkçe Kelimeler
 * N-gram modeli ve otomatik tamamlama için
 */

const TurkishDictionary = {
    // En sık kullanılan kelimeler (frekansa göre sıralı)
    commonWords: [
        // Bağlaçlar ve edatlar
        'bir', 've', 'bu', 'da', 'de', 'için', 'ile', 'gibi', 'en', 'çok',
        'daha', 'var', 'ne', 'her', 'ama', 'ya', 'veya', 'hem', 'ki', 'mi',
        'mu', 'mı', 'mü', 'ancak', 'fakat', 'lakin', 'oysa', 'halbuki', 'yani',
        'çünkü', 'zira', 'eğer', 'şayet', 'madem', 'nasıl', 'neden', 'niçin',
        
        // Zamirler
        'ben', 'sen', 'o', 'biz', 'siz', 'onlar', 'bu', 'şu', 'bunlar', 'şunlar',
        'kendi', 'birbirimiz', 'kim', 'ne', 'hangisi', 'hangi', 'kaç', 'bazı',
        'birkaç', 'hiç', 'hepsi', 'herkes', 'kimse', 'hiçbiri', 'her', 'biri',
        
        // Zarflar
        'şimdi', 'hemen', 'bugün', 'yarın', 'dün', 'sonra', 'önce', 'hâlâ',
        'henüz', 'artık', 'bazen', 'her zaman', 'asla', 'hiçbir zaman', 'yine',
        'tekrar', 'belki', 'kesinlikle', 'mutlaka', 'özellikle', 'genellikle',
        'sadece', 'yalnız', 'bile', 'hatta', 'ayrıca', 'üstelik', 'dahası',
        
        // Sıfatlar
        'iyi', 'kötü', 'güzel', 'çirkin', 'büyük', 'küçük', 'yeni', 'eski',
        'genç', 'yaşlı', 'uzun', 'kısa', 'yüksek', 'alçak', 'geniş', 'dar',
        'sıcak', 'soğuk', 'sert', 'yumuşak', 'kolay', 'zor', 'hızlı', 'yavaş',
        'doğru', 'yanlış', 'önemli', 'basit', 'karmaşık', 'farklı', 'aynı',
        
        // Fiiller (en sık kullanılanlar)
        'olmak', 'etmek', 'yapmak', 'gelmek', 'gitmek', 'vermek', 'almak',
        'demek', 'söylemek', 'görmek', 'bilmek', 'istemek', 'bulmak', 'kalmak',
        'başlamak', 'çalışmak', 'düşünmek', 'beklemek', 'anlamak', 'duymak',
        'bakmak', 'geçmek', 'tutmak', 'çıkmak', 'girmek', 'oturmak', 'kalkmak',
        'yürümek', 'koşmak', 'okumak', 'yazmak', 'dinlemek', 'konuşmak',
        'sormak', 'cevaplamak', 'yardım etmek', 'kullanmak', 'ödemek',
        
        // Mantık kelimeleri ve diğer önemli kelimeler
        'mantık', 'mantıklı', 'mantıksız', 'mantıken', 'mantıksal',
        'mümkün', 'mümkünse', 'mümkün değil', 'mümkün olmak',
        'müşteri', 'müşteri hizmetleri', 'müşteri memnuniyeti',
        'mükemmel', 'mükemmellik', 'mükemmeliyet',
        'mümkün', 'mümkünlük', 'mümkün olmak',
        'müsaade', 'müsaade etmek', 'müsaade istemek',
        'müşteri', 'müşteri desteği', 'müşteri temsilcisi',
        
        // Müşteri hizmetleri kelimeleri
        'merhaba', 'selam', 'hoşgeldiniz', 'günaydın', 'iyi günler', 'iyi akşamlar',
        'teşekkür', 'teşekkürler', 'teşekkür ederim', 'sağolun', 'rica ederim',
        'özür', 'özür dilerim', 'pardon', 'affedersiniz', 'kusura bakmayın',
        'lütfen', 'acaba', 'rica', 'müsaade', 'izin', 'yardım', 'destek',
        'sorun', 'problem', 'sıkıntı', 'arıza', 'hata', 'şikayet', 'talep',
        'sipariş', 'ürün', 'hizmet', 'fiyat', 'ücret', 'ödeme', 'fatura',
        'kargo', 'teslimat', 'iade', 'değişim', 'garanti', 'kampanya', 'indirim'
    ],

    // İki kelimelik gruplar (bigrams)
    bigrams: {
        'merhaba': ['size', 'nasıl', 'hoş', 'bugün'],
        'iyi': ['günler', 'akşamlar', 'bir', 'şekilde', 'dileklerimle'],
        'nasıl': ['yardımcı', 'olabilirim', 'bir', 'gidiyor'],
        'yardımcı': ['olabilirim', 'olmak', 'olabilir', 'olur'],
        'teşekkür': ['ederim', 'ederiz', 'ediyorum', 'ediyoruz'],
        'özür': ['dilerim', 'dileriz', 'diliyorum', 'diliyoruz'],
        'rica': ['ederim', 'ederiz', 'ediyorum'],
        'lütfen': ['bekleyin', 'bir', 'dakika', 'bilgi'],
        'bir': ['dakika', 'saniye', 'sorun', 'şey', 'an'],
        'bu': ['konuda', 'durumda', 'sorun', 'şekilde'],
        'size': ['yardımcı', 'nasıl', 'bilgi', 'en'],
        'en': ['kısa', 'yakın', 'iyi', 'hızlı', 'uygun'],
        'kısa': ['sürede', 'zamanda', 'bir'],
        'anlayışınız': ['için', 'teşekkür'],
        'talebiniz': ['için', 'alınmıştır', 'işleme'],
        'başka': ['bir', 'sorunuz', 'yardımcı'],
        'sorunuz': ['varsa', 'var', 'olursa'],
        'bilgi': ['vermek', 'almak', 'için', 'istiyorum'],
        'siparişiniz': ['için', 'hakkında', 'hazır'],
        'ödeme': ['işlemi', 'yapabilirsiniz', 'alınmıştır'],
        'müşteri': ['hizmetleri', 'temsilcisi', 'memnuniyeti'],
        'işlem': ['yapılmıştır', 'tamamlanmıştır', 'için'],
        'süre': ['içinde', 'içerisinde', 'zarfında'],
        'tekrar': ['teşekkür', 'görüşmek', 'arayabilir'],
        'güzel': ['bir', 'günler', 'haberler'],
        'değerli': ['müşterimiz', 'üyemiz', 'zamanınız'],
        'saygılarımla': ['.', ',', 'iyi', 'en'],
        'herhangi': ['bir', 'sorun', 'soru'],
        'ilgili': ['olarak', 'bilgi', 'detay'],
        'konuyla': ['ilgili', 'alakalı', 'bağlantılı'],
        'görüşmek': ['üzere', 'dileğiyle', 'isterseniz']
    },

    // Üç kelimelik gruplar (trigrams)  
    trigrams: {
        'size nasıl': ['yardımcı olabilirim', 'yardımcı olabilirm'],
        'nasıl yardımcı': ['olabilirim', 'olabilirm', 'olacağız'],
        'yardımcı olabilirim': ['?', 'bugün'],
        'teşekkür ederim': [',', '.', 'anlayışınız'],
        'özür dilerim': [',', '.', 'bu'],
        'iyi günler': [',', '.', 'dilerim'],
        'en kısa': ['sürede', 'zamanda'],
        'kısa sürede': ['sizinle', 'dönüş', 'çözüme'],
        'anlayışınız için': ['teşekkür ederiz', 'teşekkürler'],
        'başka bir': ['sorunuz', 'konuda', 'yardımcı'],
        'sorunuz varsa': ['lütfen', 'bana', 'size'],
        'rica ederim': [',', '.', 'yardımcı'],
        'müşteri hizmetleri': ['olarak', 'ekibimiz', 'birimimiz'],
        'değerli müşterimiz': [',', 'merhaba', 'hoşgeldiniz'],
        'tekrar teşekkür': ['ederim', 'ederiz'],
        'görüşmek üzere': ['.', ',', 'hoşça'],
        'ilgili olarak': ['bilgi', 'size', 'detay'],
        'bu konuda': ['size', 'yardımcı', 'bilgi']
    },

    // Kelime kökleri ve ekleri (Türkçe morfoloji)
    suffixes: {
        // İsim çekim ekleri
        noun: [
            'ler', 'lar', 'in', 'ın', 'un', 'ün', 'nin', 'nın', 'nun', 'nün',
            'e', 'a', 'ye', 'ya', 'ne', 'na', 'i', 'ı', 'u', 'ü', 'yi', 'yı',
            'yu', 'yü', 'ni', 'nı', 'nu', 'nü', 'de', 'da', 'te', 'ta', 'nde',
            'nda', 'den', 'dan', 'ten', 'tan', 'nden', 'ndan', 'le', 'la',
            'yle', 'yla', 'im', 'ım', 'um', 'üm', 'in', 'ın', 'un', 'ün',
            'iniz', 'ınız', 'unuz', 'ünüz', 'leri', 'ları'
        ],
        // Fiil çekim ekleri  
        verb: [
            'mak', 'mek', 'yor', 'iyor', 'ıyor', 'uyor', 'üyor', 'acak', 'ecek',
            'acağ', 'eceğ', 'dı', 'di', 'du', 'dü', 'tı', 'ti', 'tu', 'tü',
            'mış', 'miş', 'muş', 'müş', 'r', 'ar', 'er', 'ır', 'ir', 'ur', 'ür',
            'abil', 'ebil', 'amaz', 'emez', 'malı', 'meli', 'sa', 'se', 'arak',
            'erek', 'ınca', 'ince', 'unca', 'ünce', 'dık', 'dik', 'duk', 'dük',
            'tık', 'tik', 'tuk', 'tük', 'dığ', 'diğ', 'duğ', 'düğ'
        ],
        // Kişi ekleri
        person: [
            'im', 'ım', 'um', 'üm', 'sin', 'sın', 'sun', 'sün', 'siniz', 'sınız',
            'sunuz', 'sünüz', 'iz', 'ız', 'uz', 'üz', 'ler', 'lar', 'yim', 'yım',
            'yum', 'yüm'
        ]
    },

    // Cümle başlangıçları
    sentenceStarters: [
        'Merhaba,',
        'İyi günler,',
        'Günaydın,',
        'İyi akşamlar,',
        'Değerli müşterimiz,',
        'Sayın müşterimiz,',
        'Hoş geldiniz,',
        'Size',
        'Talebiniz',
        'Siparişiniz',
        'Ödemeniz',
        'İşleminiz',
        'Bu konuda',
        'Anlayışınız',
        'Yardımcı',
        'Lütfen',
        'Eğer',
        'Herhangi',
        'Başka'
    ],

    // Cümle sonları
    sentenceEnders: [
        'yardımcı olabilirim?',
        'için teşekkür ederiz.',
        'ederim.',
        'rica ederim.',
        'iyi günler dilerim.',
        'görüşmek üzere.',
        'saygılarımla.',
        'bilgilerinize sunarız.',
        'sizinle iletişime geçeceğiz.',
        'lütfen bizimle iletişime geçin.',
        'tamamlanmıştır.',
        'alınmıştır.'
    ],

    // Yazım düzeltmeleri
    corrections: {
        'merhba': 'merhaba',
        'mrb': 'merhaba',
        'mrba': 'merhaba',
        'slm': 'selam',
        'tesekkur': 'teşekkür',
        'tesekur': 'teşekkür',
        'tşk': 'teşekkür',
        'tşkler': 'teşekkürler',
        'tskler': 'teşekkürler',
        'ozur': 'özür',
        'lutfen': 'lütfen',
        'gnaydın': 'günaydın',
        'gnaydn': 'günaydın',
        'iyi gnler': 'iyi günler',
        'iyignler': 'iyi günler',
        'nasl': 'nasıl',
        'nasil': 'nasıl',
        'yrdm': 'yardım',
        'yardim': 'yardım',
        'musteri': 'müşteri',
        'siparis': 'sipariş',
        'urun': 'ürün',
        'fiyati': 'fiyatı',
        'odeme': 'ödeme',
        'onceki': 'önceki',
        'sonraki': 'sonraki',
        'gorusuruz': 'görüşürüz',
        'gorusmek': 'görüşmek',
        'bilgı': 'bilgi',
        'ıyı': 'iyi',
        'bılgı': 'bilgi'
    },

    // Kısaltmalar ve açılımları
    abbreviations: {
        '/mrb': 'Merhaba, size nasıl yardımcı olabilirim?',
        '/slm': 'Selam, hoş geldiniz!',
        '/gün': 'İyi günler dilerim.',
        '/tşk': 'Teşekkür ederim.',
        '/özr': 'Özür dilerim, bu durumdan dolayı.',
        '/ric': 'Rica ederim, yardımcı olmaktan memnuniyet duyarım.',
        '/bka': 'Başka bir sorunuz var mı?',
        '/güle': 'Güle güle kullanın, görüşmek üzere.',
        '/sip': 'Siparişiniz hakkında bilgi almak için lütfen sipariş numaranızı paylaşır mısınız?',
        '/öde': 'Ödeme işleminiz başarıyla tamamlanmıştır.',
        '/iad': 'İade talebiniz alınmıştır, en kısa sürede işleme alınacaktır.',
        '/bek': 'Lütfen bir dakika bekler misiniz?',
        '/kon': 'Bu konuda size yardımcı olmaktan memnuniyet duyarım.'
    }
};

// Global export
if (typeof window !== 'undefined') {
    window.TurkishDictionary = TurkishDictionary;
}
