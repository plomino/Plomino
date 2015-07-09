i18ndude rebuild-pot --pot $domain.pot --create $domain --merge $domain-manual.pot ../
i18ndude sync --pot $domain.pot */LC_MESSAGES/$domain.po
domain=plone
i18ndude sync --pot $domain-manual.pot */LC_MESSAGES/$domain.po
