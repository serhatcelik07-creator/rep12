<?php
// MCP araç tanımları: araç adı => [hub işlemi, açıklama, giriş şeması, sabit argümanlar]
// Hem uzak MCP (mcp/) hem de yerel MCP köprüsü (tools/list'i buradan alır) bunu kullanır.

declare(strict_types=1);

function hub_tool_defs(): array
{
    $s = ['type' => 'string'];
    $i = ['type' => 'integer'];
    $o = fn(array $props, array $req = []) => ['type' => 'object', 'properties' => (object)$props, 'required' => $req];

    return [
        'hub_set_project' => ['project_set',
            'MepCenter hub: Kullanıcı bir görev/proje kodu söylediğinde (örn. "matwar görevine bak", "kod matwar", '
            . '"mepcenter.com.tr/claude\'a git matwar\'a bak") HEMEN bunu çağır. Oturumu o göreve bağlar ve görevin son durumunu, '
            . 'kararları, önceki konuşmaları, dosyaları ve şu an üzerinde çalışan diğer Claude oturumlarını getirir. '
            . 'Sonra kullanıcıya nerede kalındığını kısaca söyle ve devam et.',
            $o(['code' => $s, 'name' => $s + ['description' => 'Yeni görevse isteğe bağlı açıklayıcı ad']], ['code'])],
        'hub_project_brief' => ['project_brief',
            'Bir görevin (varsayılan: bağlı olunan görev) tam özetini getirir: son durum, kararlar, konuşmalar, dosyalar, aktif oturumlar.',
            $o(['code' => $s, 'conversations' => $i + ['description' => 'Kaç son konuşma gösterilsin (varsayılan 15)']])],
        'hub_project_update' => ['project_update',
            'Görevin "son durum" notunu YENİDEN yazar (tam metin: amaç, yapılanlar, mevcut durum, sıradaki adımlar, açık sorular). '
            . 'Başka makinedeki bir Claude bu nottan devam edecek; anlamlı her aşamadan sonra güncelle.',
            $o(['summary' => $s, 'name' => $s, 'code' => $s + ['description' => 'Boşsa bağlı olunan görev']], ['summary'])],
        'hub_projects' => ['projects', 'Hub\'daki tüm görev kodlarını listeler.', $o([])],
        'hub_sessions' => ['sessions',
            'Şu an aktif tüm Claude oturumlarını listeler (makine, klasör, görev kodu, ne yaptığı). '
            . '"Mac\'te / diğer bilgisayarda ne yapılıyor?" sorularında kullan.', $o([])],
        'hub_set_status' => ['status', 'Bu oturumun ne yaptığını tek cümleyle duyurur (diğer Claude\'lar ve kullanıcı görür).',
            $o(['status' => $s], ['status'])],
        'hub_send' => ['send',
            'Mesaj gönderir. to: "admin" (kullanıcının paneli), "all", "session:ID", "machine:AD", "agent:AD", "project:KOD". '
            . 'Kullanıcı panelden yazdıysa cevabı to="admin" ile gönder.',
            $o(['to' => $s, 'topic' => $s, 'body' => $s], ['body'])],
        'hub_inbox' => ['inbox', 'Bu oturuma gelen mesajları getirir (varsayılan: yalnızca okunmamışlar).',
            $o(['unread' => $s + ['description' => '"0" verilirse okunmuşlar da gelir'], 'limit' => $i])],
        'hub_wait' => ['wait',
            'Dinleme modu: yeni mesaj gelene kadar en fazla timeout saniye (varsayılan 25) bekler. '
            . 'Kullanıcı "dinle / beklemede kal" derse döngü halinde çağır, gelen mesajı yanıtla (hub_send) ve tekrar bekle.',
            $o(['timeout' => $i])],
        'hub_log' => ['topic_add',
            'Göreve kalıcı kayıt ekler. kind: decision (karar), todo, note, summary. Önemli kararları mutlaka kaydet.',
            $o(['content' => $s, 'title' => $s, 'kind' => $s], ['content']), ['kind' => 'note']],
        'hub_topics' => ['topics',
            'Tüm oturumların kayıtlarında arar (konuşmalar, kararlar, notlar). Filtre: q, code, machine, kind, session; sayfalama: offset.',
            $o(['q' => $s, 'code' => $s, 'machine' => $s, 'kind' => $s, 'session' => $i, 'limit' => $i, 'offset' => $i])],
        'hub_topic' => ['topic', 'Bir kaydın tam içeriğini getirir. Çok uzunsa offset ile devamını oku (next_offset).',
            $o(['id' => $i, 'offset' => $i], ['id'])],
        'hub_files' => ['files', 'Hub\'a yüklenmiş dosyaları listeler (q: ad/yol, code: görev). Kullanıcının bilgisayarlarından ve panelden '
            . 'yüklenen dosyalar buradadır. İçerik için: metinse hub_file_read; Claude Code\'da hub_download; bulut oturumunda '
            . 'MEPCENTER_TOKEN ile curl (talimata bak).', $o(['q' => $s, 'code' => $s, 'limit' => $i])],
        'hub_file_read' => ['file_get', 'Hub\'daki bir metin/kod dosyasının içeriğini okur.', $o(['id' => $i], ['id']), ['format' => 'text']],
        'hub_file_delete' => ['file_delete',
            'Hub\'daki bir dosyayı siler. Dosya paylaşma protokolü: hub aktarım alanıdır, asıllar bilgisayarlarda durur; '
            . 'paslas/ altındaki aktarım dosyalarını işin bitince sil (unutulanlar birkaç gün sonra kendiliğinden silinir).',
            $o(['id' => $i], ['id'])],
        'hub_kv_set' => ['kv_set', 'Ortak veriye yazar (ns varsayılan: görev kodu). value metin veya JSON metni.',
            $o(['key' => $s, 'value' => $s, 'ns' => $s], ['key', 'value'])],
        'hub_kv_get' => ['kv_get', 'Ortak veriden okur.', $o(['key' => $s, 'ns' => $s], ['key'])],
        'hub_kv_list' => ['kv_list', 'ns verilmezse tüm alanları, verilirse o alandaki anahtarları listeler.', $o(['ns' => $s])],
        'hub_instructions' => ['instructions', 'Hub\'ın Claude ajanları için çalışma talimatını getirir.', $o([])],
    ];
}

function hub_tools_list(): array
{
    $out = [];
    foreach (hub_tool_defs() as $name => $d) {
        $out[] = ['name' => $name, 'description' => $d[1], 'inputSchema' => $d[2]];
    }
    return $out;
}

/** Bir MCP araç çağrısını çalıştırır ve Claude'a gidecek metni döndürür. */
function hub_tool_call(string $name, array $args, array $agent, array &$session): string
{
    $defs = hub_tool_defs();
    if (!isset($defs[$name])) {
        throw new HubFail("Bilinmeyen araç: $name");
    }
    [$action, , , $fixed] = $defs[$name] + [3 => []];
    $res = hub_action($action, $agent, $session, $args + $fixed); // $fixed = varsayılanlar
    // Metin döndüren işlemler okunaklı Markdown olarak verilir
    if (isset($res['brief'])) {
        return ($action === 'project_set' ? "Oturum \"{$res['code']}\" görevine bağlandı.\n\n" : '') . $res['brief'];
    }
    if ($action === 'instructions') {
        return $res['text'];
    }
    if ($action === 'file_get' && isset($res['text'])) {
        return "Dosya #{$res['id']} {$res['rel_path']} ({$res['size']} bayt)\n\n" . $res['text'];
    }
    return json_encode($res ?: ['ok' => true], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT | JSON_INVALID_UTF8_SUBSTITUTE);
}
