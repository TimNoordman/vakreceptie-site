#!/usr/bin/env python3
"""Bouwt de subpagina's van vakreceptie.nl (per dienst, per pakket en /betalen).

Gebruik:  python3 _bron/bouw.py   (vanuit de root van de repo)
Bron:     _bron/basis.css (uit index.html), _bron/pagina.css, _bron/vr.js, de inhoud hieronder.
Uitvoer:  assets/vr.css, assets/vr.js, <slug>/index.html
Formulier post naar Make-webhook 4493301 (scenario 10112994): 🔥 naar Tim + bevestigingsmail.
"""
import os, html, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(ROOT, '_bron')
E = html.escape

def incl(x):
    v = round(x * 1.21, 2)
    s = f"{v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    return s[:-3] if s.endswith(',00') else s

def eur(x):
    s = f"{x:,.0f}".replace(',', '.')
    return f"€ {s}"

# ---------- voorbeelden (met verzonnen bedrijven) ----------
def fade(t='Volledige versie na aanmelding'):
    return f'<div class="fade"><span>{t}</span></div>'

VB_AV = '''<div class="vb"><div class="doc cut">
<h4>Algemene voorwaarden De Vries Dakwerken</h4>
<div class="meta">De Vries Dakwerken · Leeuwarden · KvK 00000000 · versie 1, november 2026</div>
<h5>Artikel 1. Waar deze voorwaarden voor gelden</h5>
<p>1.1 Deze voorwaarden gelden voor alle offertes, opdrachten en werkzaamheden van De Vries Dakwerken ("wij"), voor particulieren en bedrijven ("u").</p>
<p>1.2 Afspraken die afwijken van deze voorwaarden gelden alleen als we die schriftelijk of per e-mail hebben vastgelegd.</p>
<h5>Artikel 2. Offertes</h5>
<p>2.1 Een offerte is 30 dagen geldig, tenzij in de offerte iets anders staat.</p>
<p>2.2 De offerte is gebaseerd op de informatie en foto's die u ons geeft. Blijkt de situatie ter plaatse anders, dan overleggen we voordat we verdergaan.</p>
<h5>Artikel 3. Prijzen en meerwerk</h5>
<p>3.1 Onze prijzen zijn inclusief btw voor particulieren en exclusief btw voor bedrijven, tenzij anders vermeld.</p>
<p>3.2 Meerwerk is werk dat niet in de offerte staat. We voeren meerwerk pas uit nadat u daar akkoord op hebt gegeven, en we noemen vooraf de prijs of het uurtarief.</p>
<h5>Artikel 4. Betaling</h5>
<p>4.1 U betaalt binnen 14 dagen na de factuurdatum. Bij grotere klussen kunnen we een termijnbetaling afspreken: een deel bij de start en de rest na oplevering.</p>
<p>4.2 Betaalt u niet op tijd, dan sturen we eerst een herinnering met een nieuwe termijn van 14 dagen voordat we kosten in rekening brengen.</p>
<h5>Artikel 5. Uitvoering en weer</h5>
<p>5.1 Dakwerk is afhankelijk van het weer. Bij regen, vorst of harde wind kunnen we de planning in overleg verschuiven.</p>
<p>5.2 U zorgt dat wij het dak veilig kunnen bereiken en dat er ruimte is voor materiaal en eventueel een steiger.</p>
<h5>Artikel 6. Garantie</h5>
<p>6.1 Op ons werk geven we garantie volgens de termijnen in de offerte. De garantie geldt niet bij schade door</p>
</div>''' + fade() + '</div>'

VB_WEBSITE = '''<div class="vb"><div class="browser"><i></i><i></i><i></i><span>bakkerinstallatie.nl</span></div>
<div class="site-hero"><b>Bakker Installatietechniek</b><p>Cv-ketels, warmtepompen en storingen in Amersfoort en omgeving. Storing? Binnen 24 uur bij u.</p><span class="sb">App ons op WhatsApp</span></div>
<div class="site-grid"><div><b>Cv-ketel onderhoud</b>Jaarlijks onderhoud vanaf € 89, ook op zaterdag.</div><div><b>Warmtepompen</b>Advies, plaatsing en subsidie-aanvraag in één.</div><div><b>Storing</b>24/7 bereikbaar via WhatsApp. We vragen direct naar foto's.</div></div>
<div class="site-grid" style="padding-top:0"><div><b>Werkgebied</b>Amersfoort, Leusden, Soest, Baarn en Nijkerk</div><div><b>Reviews</b>"Snel, netjes en duidelijk over de prijs." — Mevr. Jansen</div><div><b>Contact</b>Bakker Installatietechniek · KvK 00000000</div></div></div>'''

VB_REGIO = '''<div class="vb"><div class="browser"><i></i><i></i><i></i><span>dakwerkendevries.nl/dakdekker-leeuwarden</span></div>
<div class="doc" style="padding-top:28px">
<h4 style="font-size:30px">Dakdekker in Leeuwarden</h4>
<p style="color:#56616B;margin-bottom:12px">Lekkage, een nieuw plat dak of dakgoten die overlopen? De Vries Dakwerken werkt al 15 jaar in Leeuwarden en omgeving.</p>
<h5>Waar we in Leeuwarden mee helpen</h5>
<p>Platte daken (bitumen en EPDM), dakrenovatie, dakgoten en lekkagedetectie. In wijken als Huizum, Camminghaburen en het centrum kennen we de oudere daken goed.</p>
<h5>Spoed in Leeuwarden?</h5>
<p>Stuur een WhatsApp met een foto van de lekkage. U krijgt binnen een minuut antwoord en bij spoed zijn we meestal dezelfde dag ter plaatse.</p>
<p style="margin-top:14px"><span style="display:inline-block;background:#25D366;color:#073B1F;font-weight:700;border-radius:8px;padding:9px 14px;font-size:14px">App over uw dak in Leeuwarden</span></p>
<h5>Ook actief in</h5>
<p>Drachten · Franeker · Grou · Dokkum</p>
</div></div>'''

VB_TEKSTEN = '''<div class="vb"><div class="vs">
<div><div class="tag">Voor</div><h5 style="font-size:20px;margin:6px 0 8px;font-family:var(--display)">Welkom op onze website</h5><p>Wij zijn een allround installatiebedrijf met jarenlange ervaring. Wij leveren kwaliteit en service. Neem gerust contact met ons op voor meer informatie over onze mogelijkheden.</p></div>
<div><div class="tag ok">Na</div><h5 style="font-size:20px;margin:6px 0 8px;font-family:var(--display)">Cv-storing in Amersfoort? Vandaag nog geholpen.</h5><p>Bakker Installatietechniek repareert en onderhoudt cv-ketels en warmtepompen in Amersfoort, Leusden en Soest. Stuur een foto van je ketel via WhatsApp: je krijgt binnen een minuut antwoord en weet meteen wat het kost om langs te komen.</p></div>
</div></div>'''

VB_GBP = '''<div class="vb"><div class="gbp">
<div><div class="tag" style="font-family:var(--display);font-weight:700;color:#56616B;text-transform:uppercase;letter-spacing:.08em;font-size:14px">Bedrijfsbeschrijving</div>
<p>Bakker Installatietechniek is uw installateur voor cv-ketels, warmtepompen en storingen in Amersfoort, Leusden en Soest. Familiebedrijf sinds 2009, erkend installateur, en 24/7 bereikbaar via WhatsApp. Bij een storing zijn we meestal binnen 24 uur bij u.</p></div>
<div class="q"><b>Vraag: Komen jullie ook in het weekend?</b><p>Ja. Voor storingen zijn we 7 dagen per week bereikbaar. Onderhoud plannen we op werkdagen en op zaterdagochtend.</p></div>
<div class="q"><b>Vraag: Wat kost een onderhoudsbeurt?</b><p>Een standaard onderhoudsbeurt van een cv-ketel kost vanaf € 89 inclusief btw. Bij een onderhoudscontract krijgt u elk jaar automatisch een uitnodiging.</p></div>
<div><div class="tag" style="font-family:var(--display);font-weight:700;color:#56616B;text-transform:uppercase;letter-spacing:.08em;font-size:14px">Post (oktober)</div>
<p>De verwarming gaat weer aan. Laat uw cv-ketel nu nakijken, dan voorkomt u een storing in de eerste koude week. Stuur ons een WhatsApp en kies zelf een moment.</p></div>
</div></div>'''

VB_VACATURE = '''<div class="vb"><div class="doc cut" style="max-height:560px">
<h4>Allround monteur cv en warmtepompen</h4>
<div class="meta">Bakker Installatietechniek · Amersfoort · 32 tot 40 uur · fulltime of 4 × 9</div>
<p>Bij ons ben je geen nummer. Je rijdt in je eigen bus door Amersfoort en omgeving, je plant samen met ons je dag en je bent om half 5 thuis. Storingsdienst? Eén week per zes weken, en die wordt goed betaald.</p>
<h5>Wat je doet</h5>
<p>Onderhoud en storingen aan cv-ketels, plaatsen van warmtepompen, en klanten uitleggen wat je hebt gedaan.</p>
<h5>Wat we vragen</h5>
<p>Een mbo-diploma installatietechniek of vergelijkbare ervaring, rijbewijs B, en zin om te leren. Nog geen ervaring met warmtepompen? Die opleiding betalen wij.</p>
<h5>Wat je krijgt</h5>
<p>Een goed salaris, een eigen bus en gereedschap, 25 vakantiedagen en</p>
</div>''' + fade('Volledige vacature na aanmelding') + '</div>'

VB_MAIL = '''<div class="vb"><div class="mail">
<div class="hdr"><b>Van:</b> Bakker Installatietechniek &nbsp;·&nbsp; <b>Onderwerp:</b> Tijd voor je jaarlijkse cv-onderhoud</div>
<p>Beste meneer Visser,</p>
<p style="margin-top:10px">Vorig jaar hebben we in oktober uw cv-ketel nagekeken. De verwarming gaat weer aan, dus dit is een goed moment voor de volgende onderhoudsbeurt. Zo voorkomt u een storing in de eerste koude week.</p>
<p style="margin-top:10px">Kies zelf een moment dat u uitkomt, ook op zaterdagochtend:</p>
<span class="mbtn">Plan mijn onderhoud</span>
<p>Of stuur ons een WhatsApp met "onderhoud", dan plannen we het samen in.</p>
<p style="margin-top:14px">Met vriendelijke groet,<br>Bakker Installatietechniek</p>
<p style="margin-top:14px;font-size:12px;color:#8A949C">U ontvangt deze mail omdat u klant bij ons bent. Liever geen mails meer? Laat het ons weten.</p>
</div></div>'''

VB_GROEI = '''<div class="vb"><div class="doc" style="padding:28px 30px 34px">
<h4>Groeiplan De Vries Dakwerken</h4><div class="meta">Voorbeeld van de eerste drie maanden</div>
<table class="plan"><thead><tr><th>Maand</th><th>Regiopagina's</th><th>Seizoensmail</th></tr></thead><tbody>
<tr><td>November</td><td>Dakdekker Leeuwarden<br>Plat dak Drachten</td><td>Dakgoten schoonmaken voor de winter</td></tr>
<tr><td>December</td><td>Lekkage Franeker<br>Dakrenovatie Leeuwarden</td><td>–</td></tr>
<tr><td>Januari</td><td>Dakgoten Grou<br>Bitumen dak Dokkum</td><td>–</td></tr>
</tbody></table>
<p style="margin-top:12px;color:#56616B;font-size:14px">Elke maand overleggen we kort welke plaatsen en diensten de meeste klussen opleveren.</p>
</div></div>'''

def bon(stamp='SPOED'):
    return f'''<div class="bon"><header><b>Werkbon</b><span class="stamp">{stamp}</span></header><dl>
<dt>Vakgebied</dt><dd>Installateur, cv-ketel</dd><dt>Klant</dt><dd>Jeroen Visser, 3818 AB Amersfoort</dd>
<dt>Klus</dt><dd>Ketel geeft storing F28, geen warm water sinds vanochtend</dd><dt>Details</dt><dd>Remeha Calenta, ongeveer 9 jaar oud, druk 0,8 bar</dd>
<dt>Foto's</dt><dd>2 foto's van het display</dd><dt>Moment</dt><dd>Liefst vandaag na 15.00 uur</dd></dl>
<div class="tip"><b>Tip voor de vakman:</b> F28 wijst vaak op een ontstekingsprobleem. Neem een ontstekingselektrode mee.</div></div>'''

def wa(*msgs):
    out = []
    for who, txt in msgs:
        out.append(f'<div class="bub{" me" if who=="me" else ""}"><small>{"Klant" if who=="me" else "Assistent van Bakker Installatietechniek"}</small>{txt}</div>')
    return '<div class="wa-wrap">' + ''.join(out) + '</div>'

VB_START = '<div class="vb"><div class="two" style="gap:0">' + wa(
    ('me', 'Hoi, mijn cv doet het niet meer, geen warm water'),
    ('ai', 'Vervelend! Ik ben de digitale assistent van Bakker Installatietechniek. Wat staat er op het display van de ketel? Een foto mag ook.'),
    ('me', 'F28. Foto komt eraan'),
    ('ai', 'Dank je. Wat is je postcode, en wanneer kunnen we langskomen?'),
) + bon() + '</div></div>'

VB_PLUS = '<div class="vb"><div class="two" style="gap:0">' + wa(
    ('ai', '<b>3 dagen na de offerte</b><br>Hoi Jeroen, vorige week stuurden we je de offerte voor de nieuwe cv-ketel. Heb je nog vragen? Antwoord gerust hier.'),
    ('me', 'Ja, kan het ook in januari?'),
    ('ai', 'Dat geef ik direct door aan Bakker Installatietechniek. Je hoort vandaag nog of januari past.'),
) + wa(
    ('ai', '<b>Na de klus</b><br>Hoi Jeroen, de nieuwe ketel hangt. Hoe ging het? Wil je ons een review geven op Google? Dat helpt ons enorm: <u>g.page/r/bakker</u>'),
    ('me', 'Top, gedaan!'),
    ('ai', 'Dank je wel! Fijne warme winter.'),
) + '</div></div>'

VB_COMPLEET = '<div class="vb"><div class="two" style="gap:0">' + wa(
    ('ai', '<b>Onderhoud</b><br>Hoi meneer Visser, uw cv-ketel is weer aan zijn jaarlijkse beurt toe. Past dinsdag 10 november 9.00–12.00 of donderdag 12 november 13.00–16.00?'),
    ('me', 'Donderdag graag'),
    ('ai', 'Staat genoteerd: donderdag 12 november tussen 13.00 en 16.00 uur. U krijgt een bericht als de monteur onderweg is.'),
) + wa(
    ('ai', '<b>Monteur onderweg</b><br>Mark is onderweg en is rond 13.40 uur bij u.'),
    ('ai', '<b>Betaling</b><br>Hoi meneer Visser, factuur 2026-118 van € 89 staat nog open. Via deze iDEAL-link is hij zo betaald: <u>ideal-link</u>. Al betaald? Dan kunt u dit bericht negeren.'),
) + '</div></div>'

VB_PRO = '<div class="vb"><div class="doc" style="padding:28px 30px 34px"><h4>Maandoverzicht oktober</h4><div class="meta">Bakker Installatietechniek · 3 vestigingen</div>' \
    '<table class="plan"><thead><tr><th>Vestiging</th><th>Aanvragen</th><th>Spoed</th><th>Offertes opgevolgd</th><th>Nieuwe reviews</th></tr></thead><tbody>' \
    '<tr><td>Amersfoort</td><td>412</td><td>38</td><td>61</td><td>14</td></tr><tr><td>Utrecht</td><td>356</td><td>29</td><td>48</td><td>11</td></tr><tr><td>Zeist</td><td>241</td><td>17</td><td>33</td><td>8</td></tr>' \
    '</tbody></table><p style="margin-top:12px;color:#56616B;font-size:14px">Verbeterpunt voor november: in Utrecht vragen veel klanten naar warmtepomp-subsidie. We voegen een vaste uitleg toe aan de vragen.</p></div></div>'

# ---------- pagina's ----------
STAP_DIENST = [('Aanmelden', 'Vul het formulier in. Je krijgt direct een bevestiging per mail met de prijs en hoe je betaalt.'),
               ('Wij maken het', 'We vragen wat we nodig hebben en maken alles op maat voor jouw bedrijf.'),
               ('Kant-en-klaar', 'Je krijgt het resultaat om na te kijken. Wil je iets anders, dan passen we het aan.')]
STAP_PAKKET = [('Aanmelden', 'Vul het formulier in. Je krijgt direct een bevestiging met de prijs en hoe je betaalt.'),
               ('Wij richten in', 'We stellen je vragen over je vak, werkgebied en openingstijden en richten alles in. Binnen 48 uur live.'),
               ('Jij koppelt', 'Je koppelt je WhatsApp-nummer met een code. Vanaf dan wordt elke aanvraag beantwoord.')]
BETAAL_STD = 'Je krijgt een factuur van Vakreceptie. Betalen kan via de iDEAL-betaallink op de factuur of met een overboeking binnen 14 dagen.'

FAQ_PAKKET = [
    ('Zit ik ergens aan vast?', 'Nee. Elk pakket is maandelijks opzegbaar met een opzegtermijn van één maand. Je kunt ook altijd op- of afschalen.'),
    ('Blijft mijn eigen WhatsApp van mij?', 'Ja. Je gewone gesprekken met vaste klanten en leveranciers blijven van jou. De assistent reageert alleen op nieuwe aanvragen en stopt zodra jij zelf antwoordt.'),
    ('Wat als ik meer aanvragen krijg dan mijn pakket?', 'Dan nemen we eerst contact met je op. Je zit nooit vast aan onverwachte kosten.'),
    ('Is dit veilig voor de privacy van mijn klanten?', 'Ja. Elk pakket heeft een privacy- en AVG-pakket op jouw naam: privacyverklaring, verwerkingsregister, datalekprotocol en een verwerkersovereenkomst.'),
]

PAGES = []
def page(**k): PAGES.append(k)

page(slug='website', groep='Groeidiensten', kick='Website in een dag', h1='Een website<br><span>die klussen oplevert.</span>',
     lead='Geen site, of een verouderde? Binnen een dag staat er een strakke nieuwe website, met een WhatsApp-knop die direct naar je receptie gaat. Hosting erbij, zonder gedoe.',
     price=(19, 'per maand'), pricenote='24 maanden, plus € 99 start. Hosting inbegrepen.', alt='<b>Liever in één keer?</b> € 295 + € 10 per maand hosting.',
     keuzes=[('website-termijn', 'In termijnen', '€ 99 start + € 19 per maand, 24 maanden. Daarna € 10 per maand hosting.'),
             ('website-eenmalig', 'In één keer', '€ 295 eenmalig + € 10 per maand hosting, maandelijks opzegbaar.')],
     wa='PILOT: ik heb een vraag over Website in een dag', demo='WEBSITE',
     krijgt=['Een website van 1 tot 5 pagina\'s in jouw kleuren, met je logo en foto\'s', 'WhatsApp-knop die direct naar je Vakreceptie gaat', 'Teksten die wij voor je schrijven, gericht op meer aanvragen', 'Snel op mobiel, met beveiligde verbinding (https)', 'Hosting en kleine wijzigingen inbegrepen', 'Binnen 24 uur een eerste voorbeeld'],
     nodig=['Een domeinnaam op jouw naam (die vraag je zelf aan, vaak rond € 10 per jaar; wij helpen je)', 'Je logo en een paar foto\'s van je werk (heb je die niet, dan gebruiken we passende beelden)', 'Je diensten, werkgebied en contactgegevens'],
     vbt='Zo kan jouw website eruitzien', vbp='Voorbeeld met een verzonnen installateur. Jouw site krijgt je eigen naam, kleuren en foto\'s.', vb=VB_WEBSITE,
     pay=[('In termijnen', 'Start, daarna 24 maanden per maand (hosting inbegrepen)', '€ 99 + € 19/mnd'), ('In één keer', 'Eenmalig, daarna hosting per maand', '€ 295 + € 10/mnd'), ('Na 24 maanden (termijnen)', 'Alleen nog hosting, maandelijks opzegbaar', '€ 10/mnd')],
     paynote='Bij termijnen geldt een vaste looptijd van 24 maanden. Zijn alle termijnen betaald, dan krijg je op verzoek de bestanden van je site.',
     faq=[('Welke domeinnaam moet ik nemen?', 'Het liefst je bedrijfsnaam, bijvoorbeeld jouwbedrijf.nl. Je vraagt hem zelf aan bij een provider naar keuze, zodat hij altijd van jou is. Wij helpen je met de aanvraag en koppelen alles.'),
          ('Kan ik zelf teksten aanpassen?', 'Kleine wijzigingen doen wij voor je: stuur een WhatsApp of mail met wat er anders moet.'),
          ('Ik heb al een website. Kan ik die houden?', 'Ja. Dan zijn websiteteksten of regiopagina\'s misschien handiger. Die werken ook op je bestaande site.'),
          ('Wat gebeurt er als ik na de 24 maanden stop?', 'Dan zeg je de hosting op met een maand opzegtermijn. Je domeinnaam blijft van jou en je krijgt de bestanden van je site mee.')],
     related=['regiopaginas', 'websiteteksten', 'google-bedrijfsprofiel', 'groeipakket'])

page(slug='regiopaginas', groep='Groeidiensten', kick="Regiopagina's", h1='Gevonden worden<br><span>in jouw regio.</span>',
     lead='Iemand zoekt "dakdekker Leeuwarden". Met een eigen pagina per dienst en plaats sta jij ertussen, met een WhatsApp-knop om direct een aanvraag te doen.',
     price=(49, 'per pagina'), pricenote='Eenmalig per pagina. Het aantal kies je zelf.', alt="<b>Elke maand nieuwe pagina's?</b> Kijk naar het Groeipakket.",
     keuzes=[('regiopaginas', "Regiopagina's", '€ 49 per pagina. Het aantal en de plaatsen stemmen we samen af.')],
     wa="PILOT: ik heb een vraag over Regiopagina's",
     krijgt=['Per pagina één dienst in één plaats, met echte lokale tekst (geen kopie met een andere plaatsnaam)', 'WhatsApp-knop naar je Vakreceptie', 'Titel en beschrijving voor Google ingevuld', 'Op je eigen website geplaatst, of door ons gratis gehost'],
     nodig=['De diensten en plaatsen waar je meer werk wilt', 'Een paar foto\'s van klussen in de buurt (mag ook zonder)', 'Toegang tot je website, of we plaatsen ze voor je op een eigen adres'],
     vbt='Zo ziet een regiopagina eruit', vbp='Voorbeeld met een verzonnen dakdekker.', vb=VB_REGIO,
     pay=[("Regiopagina's", 'Per pagina, eenmalig', '€ 49')], paynote='Wil je elke maand twee nieuwe pagina\'s erbij? Met het Groeipakket betaal je € 99 per maand, inclusief een seizoensmail per kwartaal.',
     faq=[('Hoeveel pagina\'s heb ik nodig?', 'Begin met je belangrijkste dienst in je eigen plaats en de 3 tot 5 plaatsen eromheen. Dat is vaak genoeg om meer aanvragen te zien.'),
          ('Sta ik dan bovenaan in Google?', 'Dat kan niemand beloven. Wel vergroot een goede pagina per plaats de kans dat je gevonden wordt op zoekopdrachten uit jouw regio.'),
          ('Ik heb geen website. Kan dit toch?', 'Ja. We zetten de pagina\'s dan op een eigen adres, of je combineert ze met Website in een dag.')],
     related=['website', 'groeipakket', 'google-bedrijfsprofiel', 'websiteteksten'])

page(slug='websiteteksten', groep='Groeidiensten', kick='Websiteteksten', h1='Je site herschreven.<br><span>Voor meer aanvragen.</span>',
     lead='Veel vakbedrijven hebben een site die "kwaliteit en service" belooft maar niet zegt wat ze doen, waar en hoe je contact opneemt. Wij herschrijven hem: duidelijk, vindbaar en met één doel.',
     price=(149, 'eenmalig'), pricenote='Voor een site tot 5 pagina\'s.',
     keuzes=[('websiteteksten', 'Websiteteksten', '€ 149 eenmalig, voor een site tot 5 pagina\'s.')],
     wa='PILOT: ik heb een vraag over Websiteteksten',
     krijgt=['Nieuwe teksten voor je home- en dienstenpagina\'s', 'Koppen die zeggen wat je doet en waar', 'Titels en beschrijvingen voor Google', 'Op elke pagina een duidelijke knop om contact op te nemen', 'Eén ronde aanpassingen inbegrepen'],
     nodig=['Het adres van je website', 'Wat je het liefst doet en waar je meer werk wilt', 'Toegang om te plaatsen, of je plakt de teksten zelf'],
     vbt='Voor en na', vbp='Voorbeeld met een verzonnen installateur.', vb=VB_TEKSTEN,
     pay=[('Websiteteksten', 'Eenmalig, tot 5 pagina\'s', '€ 149')], paynote='Meer pagina\'s? Dan stemmen we de prijs vooraf met je af.',
     faq=[('Plaatsen jullie de teksten ook?', 'Ja, als je ons toegang geeft tot je website. Anders krijg je de teksten per pagina, klaar om te plakken.'),
          ('Wat als ik het niet mooi vind?', 'Eén ronde aanpassingen is inbegrepen. Zeg wat anders moet en we passen het aan.')],
     related=['website', 'regiopaginas', 'google-bedrijfsprofiel', 'algemene-voorwaarden'])

page(slug='google-bedrijfsprofiel', groep='Groeidiensten', kick='Google Bedrijfsprofiel', h1='Meer bellers<br><span>via Google Maps.</span>',
     lead='Je Google Bedrijfsprofiel is vaak het eerste wat een klant ziet. Wij zetten het op orde: beschrijving, diensten, vragen en antwoorden, en 12 posts voor het hele jaar.',
     price=(149, 'eenmalig'), pricenote='Inbegrepen in het pakket Compleet.',
     keuzes=[('google-bedrijfsprofiel', 'Google Bedrijfsprofiel op orde', '€ 149 eenmalig.')],
     wa='PILOT: ik heb een vraag over Google Bedrijfsprofiel',
     krijgt=['Een bedrijfsbeschrijving die zegt wat je doet en waar', 'De juiste categorieën en al je diensten ingevuld', '10 vragen en antwoorden die klanten echt stellen', '12 posts, één per maand, klaar om te plaatsen', 'Je WhatsApp-link als contactknop'],
     nodig=['Beheerderstoegang tot je profiel (gratis toe te voegen, wij leggen uit hoe), of je plakt de teksten zelf', 'Je diensten, werkgebied en openingstijden'],
     vbt='Zo ziet het eruit', vbp='Voorbeeld met een verzonnen installateur.', vb=VB_GBP,
     pay=[('Google Bedrijfsprofiel op orde', 'Eenmalig', '€ 149')], paynote='In het pakket Compleet zit dit al inbegrepen.',
     faq=[('Heb ik al een profiel nodig?', 'Nee. Heb je er nog geen, dan helpen we je het aan te maken. Google stuurt dan meestal een verificatiecode.'),
          ('Kunnen jullie reviews regelen?', 'We maken een link waarmee tevreden klanten makkelijk een review geven. We kopen of verzinnen nooit reviews, dat mag niet en Google haalt ze weg.')],
     related=['regiopaginas', 'website', 'websiteteksten', 'groeipakket'])

page(slug='vacaturepakket', groep='Groeidiensten', kick='Vacaturepakket', h1='Monteurs vinden<br><span>zonder cv-gedoe.</span>',
     lead='Een vacaturetekst die vakmensen aanspreekt, een vacaturepagina op je site en solliciteren via WhatsApp. Geschikt voor monteurs, leerlingen en zzp\'ers.',
     price=(99, 'eenmalig'), pricenote='Per vacature.',
     keuzes=[('vacaturepakket', 'Vacaturepakket', '€ 99 eenmalig per vacature.')],
     wa='PILOT: ik heb een vraag over het Vacaturepakket', demo='SOLLICITEER',
     krijgt=['Een vacaturetekst in de taal van vakmensen', 'Een vacaturepagina op je site of op een eigen adres', 'Solliciteren via WhatsApp: kandidaten beantwoorden een paar korte vragen', 'Een kort profiel van elke kandidaat, zonder cv', 'Tekst om te delen op Facebook, Instagram en vacaturesites'],
     nodig=['De functie, uren en wat je biedt', 'Wat je echt vraagt (diploma, rijbewijs, ervaring)', 'Een paar foto\'s van je team of bus (mag ook zonder)'],
     vbt='Zo ziet een vacature eruit', vbp='Voorbeeld met een verzonnen installateur.', vb=VB_VACATURE,
     pay=[('Vacaturepakket', 'Eenmalig per vacature', '€ 99'), ('Solliciteren via WhatsApp doorlopend', 'Optioneel, per maand', 'v.a. € 39/mnd')],
     paynote='We bewaren sollicitatiegegevens maximaal 4 weken en vragen nooit naar leeftijd, afkomst of andere beschermde kenmerken.',
     faq=[('Moeten kandidaten een cv sturen?', 'Nee. Ze beantwoorden een paar korte vragen via WhatsApp. Jij krijgt een overzichtelijk profiel en belt zelf wie je wilt spreken.'),
          ('Waar plaatsen jullie de vacature?', 'Op je eigen site of op een eigen pagina. Je krijgt teksten om zelf te delen. Betaalde vacaturesites regel je zelf, als je dat wilt.')],
     related=['website', 'regiopaginas', 'algemene-voorwaarden', 'seizoensmail'])

page(slug='algemene-voorwaarden', groep='Groeidiensten', kick='Algemene voorwaarden', h1='Voorwaarden<br><span>op jouw vak.</span>',
     lead='Betaling, meerwerk, garantie en het weer: voorwaarden die passen bij hoe jij werkt, op naam van je eigen bedrijf. Zo weet je klant vooraf waar hij aan toe is.',
     price=(79, 'eenmalig'), pricenote='Op naam van je bedrijf, voor particulieren en bedrijven.',
     keuzes=[('algemene-voorwaarden', 'Algemene voorwaarden', '€ 79 eenmalig, op naam van je bedrijf.')],
     wa='PILOT: ik heb een vraag over Algemene voorwaarden',
     krijgt=['Algemene voorwaarden op naam van je bedrijf, afgestemd op je vak', 'Afspraken over offertes, meerwerk, betaling, termijnen en garantie', 'Rekening gehouden met particuliere klanten (consumentenrecht)', 'Als Word-bestand en PDF, plus een korte versie voor onder je offerte', 'Uitleg hoe je ze geldig meestuurt'],
     nodig=['Je bedrijfsgegevens (naam, adres, KvK)', 'Hoe je werkt: betaaltermijn, aanbetaling, garantietermijnen'],
     vbt='Zo zien jouw voorwaarden eruit', vbp='Een deel van het model, met een verzonnen dakdekker. De volledige versie op jouw naam krijg je na aanmelding.', vb=VB_AV,
     pay=[('Algemene voorwaarden', 'Eenmalig, op naam van je bedrijf', '€ 79')],
     paynote='Dit is een modeldocument, geen persoonlijk juridisch advies. Werk je met grote of bijzondere opdrachten, laat ze dan nog door een jurist nakijken.',
     faq=[('Hoe maak ik mijn voorwaarden geldig?', 'Stuur ze mee met je offerte of opdrachtbevestiging, vóórdat de klant akkoord geeft. Alleen een link onderaan je mail is niet altijd genoeg. We leggen het je precies uit.'),
          ('Gelden ze ook voor particulieren?', 'Ja. De voorwaarden houden rekening met de extra bescherming die particulieren volgens de wet hebben.'),
          ('Kan ik ze later aanpassen?', 'Ja. Een kleine wijziging doen we kosteloos binnen 3 maanden.')],
     related=['vacaturepakket', 'website', 'websiteteksten', 'google-bedrijfsprofiel'])

page(slug='seizoensmail', groep='Groeidiensten', kick='Seizoensmail', h1='Je eigen klanten<br><span>weer in de agenda.</span>',
     lead='"Tijd voor je cv-onderhoud" of "Je dakgoten voor de winter": een nette mail aan je eigen klanten op het juiste moment. Wij schrijven en maken hem op, jij verstuurt hem.',
     price=(39, 'per mailing'), pricenote='Tekst en opmaak, klaar om te versturen.',
     keuzes=[('seizoensmail', 'Seizoensmail', '€ 39 per mailing.')],
     wa='PILOT: ik heb een vraag over de Seizoensmail',
     krijgt=['Een mailtekst over één onderwerp, op het juiste moment van het jaar', 'Nette opmaak in jouw kleuren, met een knop om te plannen', 'Klaar om te versturen vanuit je eigen mail of mailprogramma', 'Een korte versie voor je WhatsApp-status of social media'],
     nodig=['Het onderwerp of de dienst die je wilt promoten', 'Je logo en kleuren', 'Je klantenlijst blijft bij jou: wij krijgen die niet'],
     vbt='Zo ziet een seizoensmail eruit', vbp='Voorbeeld met een verzonnen installateur.', vb=VB_MAIL,
     pay=[('Seizoensmail', 'Per mailing', '€ 39')], paynote='Elk kwartaal een seizoensmail? Die zit in het Groeipakket.',
     faq=[('Waarom niet via WhatsApp?', 'Massaberichten via WhatsApp kunnen je nummer laten blokkeren. Een mail aan je eigen klanten is veiliger en mag gewoon, met een afmeldmogelijkheid.'),
          ('Mag ik mijn klanten zomaar mailen?', 'Bestaande klanten mag je mailen over vergelijkbare diensten, zolang je ze een makkelijke manier geeft om zich af te melden. Die regel staat er standaard in.')],
     related=['groeipakket', 'google-bedrijfsprofiel', 'regiopaginas', 'website'])

page(slug='groeipakket', groep='Groeidiensten', kick='Groeipakket', h1='Elke maand<br><span>beter gevonden.</span>',
     lead="Elke maand twee nieuwe regiopagina's en elk kwartaal een seizoensmail aan je klanten. Zonder dat jij er tijd in stopt.",
     price=(99, 'per maand'), pricenote='Maandelijks opzegbaar. Los zou het € 111 per maand kosten.',
     keuzes=[('groeipakket', 'Groeipakket', '€ 99 per maand, maandelijks opzegbaar.')],
     wa='PILOT: ik heb een vraag over het Groeipakket',
     krijgt=["Elke maand 2 nieuwe regiopagina's (dienst × plaats)", 'Elk kwartaal een seizoensmail, klaar om te versturen', 'Elke maand kort overleg over welke plaatsen en diensten de meeste klussen opleveren', 'Maandelijks opzegbaar'],
     nodig=['Je diensten en de plaatsen waar je meer werk wilt', 'Toegang tot je website, of we hosten de pagina\'s voor je'],
     vbt='Zo ziet een groeiplan eruit', vbp='Voorbeeld met een verzonnen dakdekker.', vb=VB_GROEI,
     pay=[('Groeipakket', 'Per maand, maandelijks opzegbaar', '€ 99/mnd')], paynote='Je betaalt per maand vooraf. Opzeggen kan per maand, met een maand opzegtermijn.',
     faq=[('Wat als ik geen nieuwe plaatsen meer heb?', 'Dan maken we pagina\'s voor andere diensten in je bestaande plaatsen, of we verbeteren de pagina\'s die het meeste opleveren.'),
          ('Kan ik dit combineren met een pakket?', 'Ja, het Groeipakket werkt naast elk receptiepakket.')],
     related=['regiopaginas', 'seizoensmail', 'website', 'google-bedrijfsprofiel'])

# pakketten
PK = [
 dict(slug='pakketten/start', key='start', naam='Start', sub='Rustig beginnen', m=79, s=95, aanvr=50,
      lead="Voor de zzp'er die 's avonds en in het weekend geen appjes meer wil missen. De AI-receptie beantwoordt elke aanvraag en jij krijgt een werkbon.",
      krijgt=['AI-receptie op je WhatsApp, 24/7', 'Werkbon per aanvraag', 'Spoed herkend, met veiligheidsadvies', "Foto's en spraakberichten", 'Standaard vragenlijst per vak', 'Privacy- en AVG-pakket in jouw naam', 'Support via e-mail', '50 aanvragen per maand'],
      niet=['Eigen toon en openingstijden', 'Opvolging en herinneringen'], vb=VB_START, demo='DEMO',
      vbp='Een aanvraag van een (verzonnen) klant en de werkbon die jij krijgt.'),
 dict(slug='pakketten/basis', key='basis', naam='Basis', sub='De receptie', m=99, s=195, aanvr=200,
      lead='Nooit meer een aanvraag kwijt. Elke app binnen een minuut beantwoord, met vragen die precies passen bij jouw vak, werkgebied en openingstijden.',
      krijgt=['Alles uit Start', 'Vragen ingericht op jouw vak', 'Jouw openingstijden, werkgebied en toon', "Video's en documenten", 'Vaste klanten en leveranciers met rust gelaten', 'Support via WhatsApp', '200 aanvragen per maand'],
      niet=['Offerte-opvolging en reviews'], vb=VB_START, demo='DEMO',
      vbp='Een aanvraag van een (verzonnen) klant en de werkbon die jij krijgt.'),
 dict(slug='pakketten/plus', key='plus', naam='Plus', sub='Meer opdrachten', m=149, s=195, aanvr=300, tag='Aanrader',
      lead='Haal meer uit je offertes en laat tevreden klanten voor je spreken. Plus volgt je offertes op en vraagt na elke klus om een review.',
      krijgt=['Alles uit Basis', 'Offerte-opvolging na 3 en 7 dagen', 'Google-reviews na elke klus', 'Klacht? Die komt eerst bij jou', 'Maandoverzicht van aanvragen en reacties', 'Eigen reviewlink, klaar om te delen', '300 aanvragen per maand'],
      niet=['Onderhoud, betaling en afspraken'], vb=VB_PLUS, demo='OFFERTE',
      vbp='Offerte-opvolging en een reviewverzoek bij een (verzonnen) klant.'),
 dict(slug='pakketten/compleet', key='compleet', naam='Compleet', sub='Een volle agenda', m=199, s=195, aanvr=500, tag='Beste waarde',
      lead='Je hele klantcontact geregeld, van eerste app tot betaalde factuur: onderhoud plannen, afspraken bevestigen, "monteur onderweg" en betalingsherinneringen.',
      krijgt=['Alles uit Plus', 'Onderhoudsherinneringen per jaar', 'Betalingsherinneringen met iDEAL-link', 'Afspraakbevestiging en "monteur onderweg"', 'Google Bedrijfsprofiel op orde', 'Support met voorrang', '500 aanvragen per maand'],
      niet=[], vb=VB_COMPLEET, demo='ONDERHOUD',
      vbp='Onderhoud plannen, "monteur onderweg" en een betalingsherinnering bij een (verzonnen) klant.'),
 dict(slug='pakketten/pro', key='pro', naam='Pro', sub='Voor groeiende bedrijven', m=299, s=395, aanvr='1.000+', va=True,
      lead='Voor bedrijven met meerdere vestigingen of een groot team. Alles uit Compleet, plus solliciteren via WhatsApp, tot 3 nummers en een vaste contactpersoon.',
      krijgt=['Alles uit Compleet', 'Solliciteren via WhatsApp', 'Tot 3 WhatsApp-nummers of vestigingen', '1.000+ aanvragen per maand', 'Websiteteksten herschreven', "2 regiopagina's per maand", 'Een vaste contactpersoon', 'Elke maand een verbetergesprek'],
      niet=[], vb=VB_PRO, demo='SOLLICITEER',
      vbp='Een maandoverzicht voor een (verzonnen) bedrijf met drie vestigingen.'),
]
for p in PK:
    va = 'vanaf ' if p.get('va') else ''
    page(slug=p['slug'], groep='Pakketten', kick=f"Pakket {p['naam']} · {p['sub']}", h1=f"{p['naam']}<br><span>{E(p['sub']).lower()}.</span>",
         lead=p['lead'], price=(p['m'], 'per maand'), va=p.get('va'),
         pricenote=f"+ € {p['s']} eenmalig instellen. {p['aanvr']} aanvragen per maand. Maandelijks opzegbaar.",
         keuzes=[(p['key'], f"Pakket {p['naam']}", f"{va}€ {p['m']} per maand + € {p['s']} eenmalig instellen.")],
         wa=f"PILOT {p['naam']}: " + ('graag een gesprek' if p['key'] == 'pro' else 'ik wil starten'), demo=p['demo'],
         krijgt=p['krijgt'], niet=p['niet'],
         nodig=['Je WhatsApp-nummer dat je wilt koppelen (bij voorkeur een apart zakelijk nummer)', 'Je vak, werkgebied, openingstijden en spoedprocedure', 'Je KvK-gegevens voor de opdrachtbevestiging'],
         vbt='Zo werkt het voor jouw klant', vbp=p['vbp'], vb=p['vb'], stappen=STAP_PAKKET,
         pay=[(f"Pakket {p['naam']}", 'Per maand, maandelijks opzegbaar', f"{va}€ {p['m']}/mnd"), ('Eenmalig instellen', 'Bij de start', f"€ {p['s']}")],
         paynote='De instelkosten en de eerste maand betaal je bij de start. Daarna factureren we het abonnement maandelijks vooraf.',
         faq=FAQ_PAKKET, related=[x['slug'] for x in PK if x['slug'] != p['slug']][:3] + ['groeipakket'])

NAMES = {p['slug']: (p['kick'].split(' · ')[0], ('€ %s %s' % (p['price'][0], p['price'][1]))) for p in PAGES}

# ---------- sjabloon ----------
def nav():
    return '''<nav><div class="w">
  <a class="logo" href="/" aria-label="Vakreceptie, naar de homepage"><img class="lg-l" src="/assets/logo-licht.png" alt="Vakreceptie" width="217" height="58"><img class="lg-d" src="/assets/logo-donker.png" alt="Vakreceptie" width="217" height="58"></a>
  <a class="navlink" href="/#groei">Groeien</a>
  <a class="navlink" href="/#prijs">Prijzen</a>
  <a class="navlink" href="/betalen/">Betalen</a>
  <a class="btn acc small" href="/#demo" data-wa="DEMO" target="_blank" rel="noopener">Probeer de demo</a>
</div></nav>'''

FOOT = '''<footer><div class="w">
  <span class="flogo"><img class="lg-l" src="/assets/logo-licht.png" alt="Vakreceptie" width="164" height="44"><img class="lg-d" src="/assets/logo-donker.png" alt="Vakreceptie" width="164" height="44"></span>
  <span style="user-select:all">info@vakreceptie.nl</span>
  <span style="flex-basis:100%;font-size:14px">Stone Member B.V. · Grote Markt 38, 1315 JG Almere · KvK 86739395 · btw NL864070810B01</span>
</div></footer>'''

def head(title, desc, path):
    return f'''<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="https://vakreceptie.nl/{path}">
<link rel="icon" type="image/png" sizes="64x64" href="/favicon.png">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:image" content="https://vakreceptie.nl/og.png">
<meta property="og:url" content="https://vakreceptie.nl/{path}">
<meta name="theme-color" content="#E8590C">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=Barlow:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="/assets/vr.css">
</head>
<body>
'''

def form(p):
    ks = p['keuzes']
    if len(ks) == 1:
        kz = f'<input type="hidden" name="keuze" value="{ks[0][0]}"><div class="full note" style="margin:0"><b>{E(ks[0][1])}</b>: {E(ks[0][2])} Alle bedragen excl. btw.</div>'
    else:
        kz = '<fieldset class="full keuzes" style="border:0;margin:0;padding:0"><legend style="font-weight:600;font-size:15px;margin-bottom:6px">Hoe wil je betalen?</legend>' + ''.join(
            f'<label class="keuze"><input type="radio" name="keuze" value="{k}"{" checked" if i == 0 else ""} required><div><b>{E(l)}</b><span>{E(d)}</span></div></label>' for i, (k, l, d) in enumerate(ks)) + '</fieldset>'
    return f'''<form class="aanmeld" data-wa="{E(p['wa'])}" novalidate>
{kz}
<label class="full">Bedrijfsnaam<input name="bedrijf" required maxlength="80" autocomplete="organization"></label>
<label>Rechtsvorm<select name="rechtsvorm" required><option value="">Kies…</option><option>Eenmanszaak</option><option>Vof</option><option>Bv</option><option>Anders</option></select></label>
<label>KvK-nummer<input name="kvk" required inputmode="numeric" pattern="[0-9 ]{{8,10}}" maxlength="10" title="8 cijfers"></label>
<label class="full">Straat en huisnummer<input name="adres" required maxlength="80" autocomplete="street-address"></label>
<label class="full">Postcode en plaats<input name="plaats" required maxlength="80" placeholder="1234 AB Plaats"></label>
<label><span>Je naam <em>(wie tekent)</em></span><input name="naam" required maxlength="80" autocomplete="name"></label>
<label>WhatsApp-nummer<input name="telefoon" required type="tel" maxlength="20" autocomplete="tel" placeholder="06 12345678"></label>
<label>E-mail<input name="email" required type="email" maxlength="80" autocomplete="email"></label>
<label><span>Factuur-e-mail <em>(als die anders is)</em></span><input name="factuuremail" type="email" maxlength="80"></label>
<label class="full"><span>Opmerking of vraag <em>(mag leeg)</em></span><textarea name="opmerking" maxlength="500"></textarea></label>
<label class="hp" aria-hidden="true">Laat leeg<input name="hp" tabindex="-1" autocomplete="off"></label>
<label class="full akkoord"><input type="checkbox" required> <span>We gebruiken je gegevens alleen om je aanmelding af te handelen: contact, opdrachtbevestiging en factuur. We verkopen of delen ze niet. Facturen bewaren we 7 jaar, zoals de wet vraagt.</span></label>
<div class="full" style="display:flex;flex-wrap:wrap;gap:12px;align-items:center"><button type="submit" class="btn acc">Aanmelden</button><a class="btn wa" data-wa="{E(p['wa'])}" target="_blank" rel="noopener" href="/#demo">Liever via WhatsApp</a></div>
<div class="formmsg" role="status" aria-live="polite"></div>
</form>'''

def render(p):
    amt, unit = p['price']
    va = 'v.a. ' if p.get('va') else ''
    path = p['slug'] + '/'
    crumb_grp = '<a href="/#prijs">Pakketten</a>' if p['groep'] == 'Pakketten' else '<a href="/#groei">Groeidiensten</a>'
    name = p['kick'].split(' · ')[0]
    alt = f'<p class="alt">{p["alt"]}</p>' if p.get('alt') else ''
    demo = f'<a class="btn ghost" href="/#demo" data-wa="{p["demo"]}" target="_blank" rel="noopener">Probeer de demo: {p["demo"]}</a>' if p.get('demo') else ''
    krijgt = ''.join(f'<li>{E(x)}</li>' for x in p['krijgt']) + ''.join(f'<li class="no">{E(x)}</li>' for x in p.get('niet', []))
    nodig = ''.join(f'<li>{E(x)}</li>' for x in p['nodig'])
    stappen = ''.join(f'<div class="step"><span class="n">{i}</span><h3>{E(t)}</h3><p>{E(d)}</p></div>' for i, (t, d) in enumerate(p.get('stappen', STAP_DIENST), 1))
    pay = ''.join(f'<tr><td>{E(a)}<small>{E(b)}</small></td><td>{E(c)}</td></tr>' for a, b, c in p['pay'])
    faq = ''.join(f'<details><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in p['faq'])
    rel = ''.join(f'<a href="/{s}/">{E(NAMES[s][0])}<small>{E(NAMES[s][1])}</small></a>' for s in p['related'])
    title = f"{name} · Vakreceptie"
    desc = p['lead'][:155]
    out = head(title, desc, path) + nav() + f'''
<main lang="nl">
<div class="w crumb"><a href="/">Vakreceptie</a> › {crumb_grp} › {E(name)}</div>
<section style="padding-top:8px"><div class="w ph">
  <div>
    <div class="kick">{E(p['kick'])}</div>
    <h1>{p['h1']}</h1>
    <p class="lead">{E(p['lead'])}</p>
    <div class="ctas"><a class="btn acc" href="#aanmelden">Aanmelden</a><a class="btn wa" href="/#demo" data-wa="{E(p['wa'])}" target="_blank" rel="noopener">Vraag via WhatsApp</a>{demo}</div>
  </div>
  <div class="pricebox" aria-label="Prijs">
    <span class="kick">Prijs</span>
    <span class="amt">{'<small style="margin:0 6px 0 0">v.a.</small>' if va else ''}€ {amt}<small>{E(unit)}</small></span>
    <p>{E(p['pricenote'])}</p>
    <p>Excl. btw (€ {incl(amt)} incl. btw).</p>
    {alt}
  </div>
</div></section>

<section><div class="w two">
  <div class="card"><h2>Wat je krijgt</h2><ul class="checks">{krijgt}</ul></div>
  <div class="card"><h2>Wat we van je nodig hebben</h2><ul class="checks need">{nodig}</ul></div>
</div></section>

<section><div class="w">
  <div class="vbhead"><div><div class="kick">Voorbeeld</div><h2>{E(p['vbt'])}</h2></div><p>{E(p['vbp'])}</p></div>
  {p['vb']}
</div></section>

<section><div class="w">
  <div class="kick">Zo werkt het</div><h2>In drie stappen</h2>
  <div class="steps">{stappen}</div>
</div></section>

<section><div class="w two">
  <div class="card"><h2>Prijs en betalen</h2>
    <table class="paytbl"><tbody>{pay}</tbody></table>
    <p class="muted" style="margin-top:10px;font-size:15px">Alle bedragen excl. 21% btw.</p>
    <div class="pays"><span>iDEAL-betaallink</span><span>Overboeking binnen 14 dagen</span>{'<span>In termijnen</span>' if any('termijn' in k[0] for k in p['keuzes']) else ''}</div>
    <p style="margin-top:14px">{E(BETAAL_STD)}</p>
    <div class="note">{E(p['paynote'])}</div>
    <p style="margin-top:12px"><a href="/betalen/" style="color:var(--accent);font-weight:600">Alles over betalen ›</a></p>
  </div>
  <div><div class="kick">Veelgestelde vragen</div><h2 style="margin-bottom:16px">Goed om te weten</h2>{faq}</div>
</div></section>

<section id="aanmelden"><div class="w formwrap">
  <div><div class="kick">Aanmelden</div><h2>Zin om te beginnen?</h2>
    <p class="lead" style="font-size:18px;margin-top:14px">Vul je gegevens in. Je krijgt direct een bevestiging per mail met je keuze, de prijs en hoe je betaalt. Daarna neemt iemand van het Vakreceptie-team persoonlijk contact met je op.</p>
    <p class="muted" style="margin-top:14px;font-size:15px">Nog een vraag? Stuur ons een WhatsApp-bericht, je krijgt dezelfde dag antwoord.</p>
  </div>
  {form(p)}
</div></section>

<section style="padding-top:8px"><div class="w"><div class="kick">Bekijk ook</div><div class="related">{rel}</div></div></section>
</main>
''' + FOOT + '\n<script src="/assets/vr.js" defer></script>\n</body>\n</html>\n'
    return out

def betalen():
    rows = ''.join(f'<tr><td>Pakket {p["naam"]}<small>Per maand, + € {p["s"]} eenmalig instellen</small></td><td>{"v.a. " if p.get("va") else ""}€ {p["m"]}/mnd</td></tr>' for p in PK)
    return head('Betalen · Vakreceptie', 'Hoe je betaalt bij Vakreceptie: iDEAL-betaallink, overboeking, per maand of in termijnen. Alle prijzen excl. btw.', 'betalen/') + nav() + f'''
<main lang="nl">
<div class="w crumb"><a href="/">Vakreceptie</a> › Betalen</div>
<section style="padding-top:8px"><div class="w">
  <div class="kick">Betalen</div>
  <h1 style="font-size:clamp(44px,7vw,80px);font-weight:800;text-transform:uppercase;margin:10px 0 16px">Betalen<br><span style="color:var(--accent)">zoals jij wilt.</span></h1>
  <p class="lead">Je krijgt altijd een factuur van Vakreceptie. Betalen kan met een iDEAL-betaallink of met een gewone overboeking. Abonnementen betaal je per maand, grotere bedragen zoals een website ook in termijnen.</p>
</div></section>
<section><div class="w two">
  <div class="card"><h2>Zo kun je betalen</h2><ul class="checks">
    <li>iDEAL-betaallink: op elke factuur, betaald in een paar tikken</li>
    <li>Overboeking binnen 14 dagen na de factuurdatum</li>
    <li>Abonnementen per maand vooraf, maandelijks opzegbaar</li>
    <li>Website in 24 termijnen: € 99 start + € 19 per maand</li>
  </ul>
  <div class="note">Alle prijzen op deze site zijn exclusief 21% btw. Op de factuur staat de btw er apart bij.</div></div>
  <div class="card"><h2>Wat betaal je wanneer?</h2><table class="paytbl"><tbody>
    <tr><td>Pakketten<small>Instelkosten en de eerste maand bij de start, daarna elke maand vooraf</small></td><td>per maand</td></tr>
    <tr><td>Eenmalige diensten<small>Na oplevering, binnen 14 dagen</small></td><td>eenmalig</td></tr>
    <tr><td>Website in termijnen<small>Start bij oplevering, daarna 24 maanden</small></td><td>€ 99 + € 19/mnd</td></tr>
    <tr><td>Te laat betaald?<small>Eerst een herinnering met 14 dagen extra, daarna kan de dienst tijdelijk stoppen</small></td><td>–</td></tr>
  </tbody></table></div>
</div></section>
<section><div class="w two">
  <div class="card"><h2>Pakketten</h2><table class="paytbl"><tbody>{rows}</tbody></table><p style="margin-top:12px"><a href="/#prijs" style="color:var(--accent);font-weight:600">Vergelijk alle pakketten ›</a></p></div>
  <div class="card"><h2>Domeinnaam en e-mail</h2><p>Je domeinnaam (bijvoorbeeld jouwbedrijf.nl) en je zakelijke e-mailadres vraag je zelf aan bij een provider naar keuze. Een .nl-domein kost vaak rond € 10 per jaar. Zo staan ze altijd op jouw naam en blijven ze van jou.</p><p style="margin-top:10px">Wij helpen je met de aanvraag en koppelen alles aan je website en Vakreceptie.</p></div>
</div></section>
<section><div class="w"><div class="kick">Bekijk ook</div><div class="related">
  <a href="/website/">Website in een dag<small>€ 19 per maand</small></a><a href="/pakketten/plus/">Pakket Plus<small>€ 149 per maand</small></a><a href="/groeipakket/">Groeipakket<small>€ 99 per maand</small></a><a href="/algemene-voorwaarden/">Algemene voorwaarden<small>€ 79 eenmalig</small></a>
</div></div></section>
</main>
''' + FOOT + '\n<script src="/assets/vr.js" defer></script>\n</body>\n</html>\n'

def main():
    os.makedirs(os.path.join(ROOT, 'assets'), exist_ok=True)
    css = open(os.path.join(B, 'basis.css')).read() + open(os.path.join(B, 'pagina.css')).read()
    open(os.path.join(ROOT, 'assets/vr.css'), 'w').write(css)
    open(os.path.join(ROOT, 'assets/vr.js'), 'w').write(open(os.path.join(B, 'vr.js')).read())
    for p in PAGES:
        d = os.path.join(ROOT, p['slug']); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w').write(render(p))
    d = os.path.join(ROOT, 'betalen'); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w').write(betalen())
    print(len(PAGES) + 1, 'pagina\'s gebouwd')

if __name__ == '__main__':
    main()
