#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# Video Pipeline — for GitHub Actions + Local
# Reads .md files → downloads from source → transcodes → uploads to B2
# ═══════════════════════════════════════════════════════════════
set -u

# ── CONFIG (env-overridable) ──
COOKIES="${VIMEO_COOKIES:-$HOME/videos/cookies.txt}"
WORK="${WORK:-/tmp/videos}"
B2_BUCKET="${B2_BUCKET:-b2:yousef-films}"
B2_CDN="${B2_CDN:-https://b2-video.mohamedyou1357.workers.dev}"
QUALITIES="${QUALITIES:-720 480 360}"
PRESET="${PRESET:-fast}"
CRF="${CRF:-23}"
COOKIE_WARN_DAYS="${COOKIE_WARN_DAYS:-90}"
LOG="$WORK/pipeline.log"

mkdir -p "$WORK"
> "$LOG"

G=$'\033[0;32m'; Y=$'\033[0;33m'; R=$'\033[0;31m'; B=$'\033[0;34m'; N=$'\033[0m'
log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG"; }
ok()   { echo "${G}✅ $*${N}"; }
warn() { echo "${Y}⚠  $*${N}"; }
err()  { echo "${R}❌ $*${N}"; }
info() { echo "${B}ℹ  $*${N}"; }


# ── Cookie age checker ──
check_cookies_age() {
  [ -f "$COOKIES" ] || return 0
  local mtime
  # macOS / Linux compatible stat
  mtime=$(stat -c %Y "$COOKIES" 2>/dev/null || stat -f %m "$COOKIES" 2>/dev/null || echo 0)
  [ "$mtime" -eq 0 ] && return 0

  local age_days=$(( ($(date +%s) - mtime) / 86400 ))

  if [ "$age_days" -ge "$COOKIE_WARN_DAYS" ]; then
    echo ""
    warn "⚠️  Cookies عمرها ${age_days} يوم — قد تحتاج تجديد قريبًا"
    warn "   (العتبة: $COOKIE_WARN_DAYS يوم)"
    warn "   جدّدها من: Firefox → Get cookies.txt LOCALLY"
    warn "   ثم: base64 -i cookies.txt | pbcopy → update GitHub secret"
    echo ""
  else
    info "🍪 Cookies عمرها ${age_days} يوم (< $COOKIE_WARN_DAYS) — سليمة"
  fi
}

resolve_source() {
  local src="$1"
  case "$src" in
    vimeo:*)     echo "https://vimeo.com/${src#vimeo:}" ;;
    youtube:*)   echo "${src#youtube:}" ;;
    twitter:*)   echo "${src#twitter:}" ;;
    x:*)         echo "${src#x:}" ;;
    instagram:*) echo "${src#instagram:}" ;;
    tiktok:*)    echo "${src#tiktok:}" ;;
    facebook:*)  echo "${src#facebook:}" ;;
    fb:*)        echo "${src#fb:}" ;;
    dailymotion:*) echo "${src#dailymotion:}" ;;
    reddit:*)    echo "${src#reddit:}" ;;
    snapchat:*)  echo "${src#snapchat:}" ;;
    linkedin:*)  echo "${src#linkedin:}" ;;
    streamable:*) echo "${src#streamable:}" ;;
    raw:*)       echo "${src#raw:}" ;;
    http*)       echo "$src" ;;
    [0-9]*)      echo "https://vimeo.com/$src" ;;
    *)           echo "$src" ;;
  esac
}

parse_md() {
  local f="$1"
  local slug id title src
  slug=$(grep -m1 '^videoSlug:' "$f" | sed 's/.*videoSlug: *//; s/[ "]*$//')
  if [ -z "$slug" ]; then
    slug=$(basename "$f" .md | sed 's/^short-film-//' \
           | sed -E 's/([a-z0-9])([A-Z])/\1-\2/g' \
           | tr '[:upper:]' '[:lower:]' \
           | sed 's/[^a-z0-9-]/-/g; s/--*/-/g; s/^-\|-$//g')
  fi
  title=$(grep -m1 '^title:' "$f" | sed 's/.*title: *//; s/^"//; s/"$//')
  src=$(grep -m1 '^videoSource:' "$f" | sed 's/.*videoSource: *//; s/^"//; s/"$//')
  if [ -z "$src" ]; then
    id=$(grep -m1 '^vimeoId:' "$f" | sed 's/.*vimeoId: *//; s/[ "]*$//')
    [ -n "$id" ] && src="vimeo:$id"
  fi
  if [ -z "$src" ]; then
    src=$(grep -m1 '^videoUrl:' "$f" | sed 's/.*videoUrl: *//; s/^"//; s/"$//')
  fi
  [ -z "$src" ] && return 1
  echo "$slug|$src|$title"
}

parse_md_folder() {
  local dir="$1" f line
  for f in "$dir"/*.md; do
    [ -f "$f" ] || continue
    case "$(basename "$f")" in
      short-film-*) ;;
      *) continue ;;
    esac
    line=$(parse_md "$f") || continue
    echo "$line"
  done
}

is_complete() {
  local slug="$1" src="$2" h found=0 total=0

  # 1. هل كل الجودات موجودة؟
  local remote
  remote=$(rclone lsf "$B2_BUCKET/$slug/" 2>/dev/null)
  for h in $QUALITIES; do
    total=$((total+1))
    echo "$remote" | grep -q "${slug}-${h}\.mp4" && found=$((found+1))
  done
  [ "$found" -lt "$total" ] && return 1

  # 2. هل المصدر لم يتغير؟ (مقارنة .videosrc على B2)
  local remote_marker
  remote_marker=$(rclone cat "$B2_BUCKET/$slug/.videosrc" 2>/dev/null | tr -d '
')
  [ "$remote_marker" = "$src" ] && return 0

  # المصدر تغيّر → إعادة معالجة
  return 1
}

download() {
  local slug="$1" src="$2"
  local url; url=$(resolve_source "$src")
  local raw="$WORK/$slug-raw.mp4"
  [ -f "$raw" ] && { info "[$slug] raw موجود"; return 0; }
  info "[$slug] ⬇  $url"
  local ck=(); [ -f "$COOKIES" ] && ck=(--cookies "$COOKIES")
  local dl_log="$WORK/$slug-download.log"
  if yt-dlp "${ck[@]}" --no-playlist \
    --format "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best" \
    --merge-output-format mp4 --no-warnings \
    --retries 10 --fragment-retries 10 \
    --socket-timeout 30 \
    --concurrent-fragments 4 \
    -o "$WORK/${slug}-raw.%(ext)s" "$url" > "$dl_log" 2>&1; then
    [ -f "$raw" ] && return 0
  fi
  err "[$slug] download فشل — آخر 15 سطر من yt-dlp:"
  tail -40 "$dl_log" | sed 's/^/    /'
  return 1
}

transcode() {
  local slug="$1" h="$2"
  local raw="$WORK/$slug-raw.mp4"
  local outdir="$WORK/$slug"
  local out="$outdir/${slug}-${h}.mp4"
  mkdir -p "$outdir"
  [ -f "$out" ] && return 0
  local abr=96; [ "$h" -ge 540 ] && abr=128
  info "[$slug] 🎞  ${h}p"
  ffmpeg -i "$raw" -c:v libx264 -preset "$PRESET" -crf "$CRF" \
    -vf "scale=-2:$h" -c:a aac -b:a "${abr}k" \
    -movflags +faststart -y "$out" >> "$LOG" 2>&1
}

upload() {
  local slug="$1"
  local src="$2"
  local outdir="$WORK/$slug"
  [ -d "$outdir" ] || return 1
  info "[$slug] ☁  رفع"
  rclone copy "$outdir" "$B2_BUCKET/$slug/" --no-traverse >> "$LOG" 2>&1

  # اكتب marker يحتوي على المصدر (vimeoId أو videoSource)
  echo -n "$src" > "$WORK/$slug.videosrc"
  rclone copyto "$WORK/$slug.videosrc" "$B2_BUCKET/$slug/.videosrc" >> "$LOG" 2>&1
}

process_video() {
  local slug="$1" src="$2" title="$3"
  echo ""
  echo "════════════════════════════════════════"
  echo "🎬  [$slug] $title"
  echo "════════════════════════════════════════"

  if is_complete "$slug" "$src"; then
    ok "[$slug] موجود على B2 + المصدر لم يتغير — تخطي"
    return 0
  fi

  # إذا الملفات موجودة لكن المصدر تغير → حذف القديم أولًا
  if rclone lsf "$B2_BUCKET/$slug/" 2>/dev/null | grep -q "\.mp4$"; then
    warn "[$slug] المصدر تغيّر — حذف النسخة القديمة من B2"
    rclone purge "$B2_BUCKET/$slug/" >> "$LOG" 2>&1
    rm -rf "$WORK/$slug" "$WORK/$slug-raw.mp4" 2>/dev/null
  fi

  download "$slug" "$src" || { err "[$slug] download فشل"; return 1; }

  local h
  for h in $QUALITIES; do
    transcode "$slug" "$h" || { err "[$slug] ${h}p فشل"; return 1; }
  done

  upload "$slug" "$src" || { err "[$slug] upload فشل"; return 1; }
  ok "[$slug] اكتمل"
}

main() {
  local md_folder=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --md) md_folder="$2"; shift 2;;
      *)    md_folder="$1"; shift;;
    esac
  done

  echo "════════════════════════════════════════"
  echo "  Video Pipeline"
  echo "  Qualities: $QUALITIES"
  echo "  Bucket:    $B2_BUCKET"
  echo "  CDN:       $B2_CDN"
  echo "════════════════════════════════════════"

  # فحص عمر cookies
  check_cookies_age

  local entries=()
  if [ -n "$md_folder" ]; then
    info "قراءة .md من: $md_folder"
    while IFS= read -r line; do entries+=("$line"); done < <(parse_md_folder "$md_folder")
  fi

  info "عدد الفيديوهات: ${#entries[@]}"
  echo ""

  local failed=() start=$(date +%s)

  for entry in "${entries[@]}"; do
    IFS='|' read -r slug src title <<< "$entry"
    process_video "$slug" "$src" "$title" || failed+=("$slug")
  done

  local end=$(date +%s)
  local dur=$(( (end-start)/60 ))

  echo ""
  echo "════════════════════════════════════════"
  echo "🎉  اكتمل في ${dur} دقيقة"
  echo "════════════════════════════════════════"
  [ ${#failed[@]} -gt 0 ] && err "فشل: ${failed[*]}" || ok "كل الفيديوهات نجحت"
  echo ""
  rclone size "$B2_BUCKET/"

  # ── macOS Notification (only on local Mac) ──
  if [[ "$OSTYPE" == "darwin"* ]] && command -v osascript &>/dev/null; then
    if [ ${#failed[@]} -eq 0 ]; then
      osascript -e "display notification \"اكتملت معالجة ${#entries[@]} فيديو في ${dur} دقيقة\" with title \"Video Pipeline ✅\" sound name \"Glass\"" 2>/dev/null || true
    else
      osascript -e "display notification \"فشل ${#failed[@]} من ${#entries[@]} فيديو\" with title \"Video Pipeline ❌\" sound name \"Basso\"" 2>/dev/null || true
    fi
  fi

  # ── GitHub Actions Summary ──
  if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
    {
      echo "## 🎬 Video Pipeline — النتيجة"
      echo ""
      echo "- **عدد الفيديوهات:** ${#entries[@]}"
      echo "- **فشل:** ${#failed[@]}"
      echo "- **المدة:** ${dur} دقيقة"
    } >> "$GITHUB_STEP_SUMMARY"
  fi
}

main "$@"
