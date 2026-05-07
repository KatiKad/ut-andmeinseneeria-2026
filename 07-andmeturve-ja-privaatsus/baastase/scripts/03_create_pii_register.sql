\echo 'Loon PII registri governance.pii_register.'

-- See tabel ei ole kogu andmekataloog ega andmetöötlusregister.
-- See on praktikumi väike PII klassifitseerimise tabel: iga rida kirjeldab üht veergu.
-- Päris projektis hoitakse sellist infot sageli andmekataloogis või andmehalduse tööriistas.
CREATE TABLE IF NOT EXISTS governance.pii_register (
    sort_order INTEGER PRIMARY KEY,
    schema_name TEXT NOT NULL,
    table_name TEXT NOT NULL,
    column_name TEXT NOT NULL,
    pii_category TEXT NOT NULL CHECK (pii_category IN ('otsene PII', 'kaudne PII', 'ei ole PII')),
    reason TEXT NOT NULL,
    handling_note TEXT NOT NULL
);

-- Registri sisu ehitatakse iga käivitusega uuesti.
-- Nii saab skripti parandada ja uuesti käivitada ilma käsitsi koristamata.
TRUNCATE TABLE governance.pii_register;

-- Iga INSERT rida kirjeldab üht toortabeli veergu.
-- pii_category eristab otsest PII-d, kaudset PII-d ja mitte-PII välju.
-- handling_note aitab hiljem otsustada, kas välja näidata, maskeerida või koondada.
INSERT INTO governance.pii_register
    (sort_order, schema_name, table_name, column_name, pii_category, reason, handling_note)
VALUES
    (1, 'staging', 'osalejad_raw', 'osaleja_id', 'kaudne PII',
     'Sisemine tunnus ei ole nimi, kuid sama inimest saab selle abil ridades kokku viia.',
     'Jaga ainult siis, kui roll vajab reataseme seostamist.'),
    (2, 'staging', 'osalejad_raw', 'eesnimi', 'otsene PII',
     'Eesnimi aitab inimest tuvastada, eriti koos teiste väljadega.',
     'Maskeeri või jäta väljast välja.'),
    (3, 'staging', 'osalejad_raw', 'perenimi', 'otsene PII',
     'Perenimi aitab inimest tuvastada, eriti koos eesnimega.',
     'Maskeeri või jäta väljast välja.'),
    (4, 'staging', 'osalejad_raw', 'email', 'otsene PII',
     'E-posti aadress võib inimest otse tuvastada.',
     'Maskeeri või anna ainult eriloaga rollile.'),
    (5, 'staging', 'osalejad_raw', 'telefon', 'otsene PII',
     'Telefoninumber võib inimest otse tuvastada.',
     'Maskeeri või jäta väljast välja.'),
    (6, 'staging', 'osalejad_raw', 'linn', 'kaudne PII',
     'Linn ei pruugi üksi inimest tuvastada, kuid koos kursuse ja nimega võib risk suureneda.',
     'Luba analüüsiks vajaduse korral, kuid ära lisa nime ja kontakti juurde.'),
    (7, 'staging', 'osalejad_raw', 'maakond', 'kaudne PII',
     'Maakond on üldisem kui linn, kuid võib koos teiste väljadega olla tuvastav.',
     'Sobib koondaruannetesse.'),
    (8, 'staging', 'osalejad_raw', 'kursus', 'ei ole PII',
     'Kursuse nimetus ei tuvasta inimest ilma teiste väljadeta.',
     'Sobib analüüsiks ja koondaruannetesse.'),
    (9, 'staging', 'osalejad_raw', 'staatus', 'kaudne PII',
     'Staatus võib olla tundlik, kui see on seotud konkreetse inimesega.',
     'Kasuta reatasemel ettevaatlikult ja koondites vabamalt.'),
    (10, 'staging', 'osalejad_raw', 'registreerumise_kuupaev', 'kaudne PII',
     'Kuupäev võib koos teiste tunnustega aidata inimest eristada.',
     'Vajadusel ümarda kuu või nädalani.');

\echo 'PII register on valmis.'

-- Viimane päring näitab registrit õppijale kohe pärast loomist.
SELECT column_name, pii_category, handling_note
FROM governance.pii_register
ORDER BY sort_order;
