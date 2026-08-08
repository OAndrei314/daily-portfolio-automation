<#
.SYNOPSIS
  Generates a local HTML rundown of everything merged across the OAndrei314 GitHub
  portfolio in the trailing 7 days, and writes it to a local folder.

.DESCRIPTION
  Pure data pull + template render -- no LLM involved, so it's fast, free, and fully
  deterministic. Meant to run on a weekly Windows Task Scheduler trigger, independent of
  the daily GitHub Actions automation (which runs in the cloud and cannot write to this
  machine's disk -- that's the whole reason this script exists locally instead).

  Requires: gh CLI, already authenticated (uses the same auth this machine already has).

.NOTES
  Maintained by: claude-actions-daily-routine (local weekly-report companion script)
#>

$ErrorActionPreference = "Stop"

$since = (Get-Date).ToUniversalTime().AddDays(-7).ToString("yyyy-MM-dd")
$today = (Get-Date).ToString("yyyy-MM-dd")
$account = "OAndrei314"

Write-Output "Fetching PRs merged since $since for $account..."

$raw = gh search prs --owner $account --merged --merged-at ">=$since" --json title,url,repository,closedAt --limit 200
$items = $raw | ConvertFrom-Json

Write-Output "Found $($items.Count) merged PR(s)."

# Group by owning repo, sorted by repo name
$byRepo = $items | Group-Object { $_.repository.name } | Sort-Object Name

function HtmlEscape([string]$s) {
    if ($null -eq $s) { return "" }
    return [System.Net.WebUtility]::HtmlEncode($s)
}

$reposHtml = ""
foreach ($grp in $byRepo) {
    $prItems = ""
    foreach ($pr in ($grp.Group | Sort-Object closedAt)) {
        $mergedDate = ([datetime]$pr.closedAt).ToString("yyyy-MM-dd")
        $title = HtmlEscape($pr.title)
        $url = HtmlEscape($pr.url)
        $prItems += "      <li><a href=`"$url`">$title</a> <span class=`"date`">merged $mergedDate</span></li>`n"
    }
    $repoName = HtmlEscape($grp.Name)
    $reposHtml += @"
    <section>
      <h2>$repoName <span class="count">($($grp.Count))</span></h2>
      <ul>
$($prItems.TrimEnd())
      </ul>
    </section>

"@
}

if ($byRepo.Count -eq 0) {
    $reposHtml = "    <p class=`"empty`">No PRs merged across the portfolio in the last 7 days.</p>"
}

$totalCount = $items.Count
$repoCount = $byRepo.Count

$html = @"
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Portfolio weekly rundown - $today</title>
<style>
  :root { color-scheme: light dark; }
  body {
    font-family: -apple-system, "Segoe UI", sans-serif;
    max-width: 760px; margin: 40px auto; padding: 0 16px;
    line-height: 1.5;
  }
  h1 { font-size: 1.6rem; margin-bottom: 0.2rem; }
  .meta { color: #666; font-size: 0.92rem; margin-top: 0; }
  .summary {
    display: flex; gap: 24px; margin: 20px 0 32px;
    padding: 14px 18px; border: 1px solid #ddd; border-radius: 8px;
  }
  .summary div { text-align: center; }
  .summary .num { font-size: 1.4rem; font-weight: 600; display: block; }
  .summary .label { font-size: 0.8rem; color: #666; }
  h2 { font-size: 1.05rem; margin-top: 1.8rem; border-bottom: 1px solid #ddd; padding-bottom: 6px; }
  .count { color: #888; font-weight: 400; font-size: 0.85em; }
  ul { padding-left: 1.2rem; }
  li { margin: 6px 0; }
  .date { color: #888; font-size: 0.85em; }
  .empty { color: #666; font-style: italic; }
  a { color: inherit; }
</style>
</head>
<body>
  <h1>Portfolio weekly rundown</h1>
  <p class="meta">Merged PRs across all $account repos, $since &rarr; $today.</p>
  <div class="summary">
    <div><span class="num">$totalCount</span><span class="label">PRs merged</span></div>
    <div><span class="num">$repoCount</span><span class="label">repos touched</span></div>
  </div>
$reposHtml
</body>
</html>
"@

$outDir = Join-Path $env:USERPROFILE "Documents\github_projects\weekly-reports"
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }

$outFile = Join-Path $outDir "weekly-$today.html"
$latestFile = Join-Path $outDir "latest.html"

$html | Out-File -FilePath $outFile -Encoding utf8
$html | Out-File -FilePath $latestFile -Encoding utf8

Write-Output "Wrote $outFile"
Write-Output "Wrote $latestFile"
