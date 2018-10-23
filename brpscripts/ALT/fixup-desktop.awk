#!/bin/awk -f
BEGIN {FS = "="}
# 1. Encoding=UTF-8
// {printline=1}
/^Encoding=UTF-8$/ {printline=0}
# 2. Icon= .png/svg/xpm cleanup if not absolute
/^Icon=[^/].*\.(png|svg|xpm)$/ {sub (/\.(png|svg|xpm)$/,"")}
# 3. trailing ; in MimeType=, Category=
/^MimeType=.*[^[:blank:];][[:blank:]]*$/ {$0=$0 ";"}
/^Categories=.*[^[:blank:];][[:blank:]]*$/ {$0=$0 ";"}
# 4. Category: subst Desktop -> X-Desktop and so on
# kill Application; in category
/^Categories=/ {
    split($2, a, ";")
    $0=$1 "="
    for (i = 1; i <= length(a); i++)
    {
	if (a[i] != "") {
	    sub (/^Typing$/,"X-Typing", a[i])
	    sub (/^Desktop$/,"X-Desktop", a[i])
	    sub (/^VideoSettings$/,"X-ALTLinux-VideoSettings", a[i])
	    sub (/^PersonalSettings$/,"X-PersonalSettings", a[i])
	    sub (/^PDFViewer$/,"X-PDFViewer", a[i])
	    if (a[i] != "Application" || length(a) <= 2)
		$0=$0 a[i] ";"
	}
    }
}
// {if (printline) print $0}
