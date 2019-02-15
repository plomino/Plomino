CATALOGNAME="Products.CMFPlomino"

# List of languages
LANGUAGES="cs de en es fr it lt"

# Create locales folder structure for languages
for lang in $LANGUAGES; do
    install -d $lang/LC_MESSAGES
done

# Rebuild .pot
i18ndude rebuild-pot --pot $CATALOGNAME.pot \
    --create $CATALOGNAME \
    --merge $CATALOGNAME-manual.pot \
    ../

# Compile po files
for lang in $(find ../locales -mindepth 1 -maxdepth 1 -type d); do

    if test -d $lang/LC_MESSAGES; then

        PO=$lang/LC_MESSAGES/${CATALOGNAME}.po

        # Create po file if not exists
        touch $PO

        # Sync po file
        echo "Syncing $PO"
        i18ndude sync --pot $CATALOGNAME.pot $PO

        # Compile .po to .mo
        MO=$lang/LC_MESSAGES/${CATALOGNAME}.mo
        echo "Compiling $MO"
        msgfmt -o $MO $lang/LC_MESSAGES/${CATALOGNAME}.po
    fi
done

# Synchronise the templates and scripts with the .pot.
i18ndude rebuild-pot --pot plone.pot \
    --create plone \
    ../configure.zcml \
    ../profiles/default/

# Synchronise the Plone's pot file (Used for the workflows)
for po in ../locales/*/LC_MESSAGES/plone.po; do
    i18ndude sync --pot plone.pot $po

    # Compile .po to .mo
    MO=$lang/LC_MESSAGES/plone.mo
    echo "Compiling $MO"
    msgfmt -o $MO $lang/LC_MESSAGES/plone.po
done

ERRORS=`find ../ -name "*pt" | xargs i18ndude find-untranslated | grep -e '^-ERROR' | wc -l`
WARNINGS=`find ../ -name "*pt" | xargs i18ndude find-untranslated | grep -e '^-WARN' | wc -l`
FATAL=`find ../ -name "*pt"  | xargs i18ndude find-untranslated | grep -e '^-FATAL' | wc -l`

echo
echo "There are $ERRORS errors \(almost definitely missing i18n markup\)"
echo "There are $WARNINGS warnings \(possibly missing i18n markup\)"
echo "There are $FATAL fatal errors \(template could not be parsed, eg. if it\'s not html\)"
echo "For more details, run \'find . -name \"\*pt\" \| xargs i18ndude find-untranslated\' or" 
echo "Look the rebuild i18n log generate for this script called \'rebuild_i18n.log\' on locales dir" 

rm ./rebuild_i18n.log
touch ./rebuild_i18n.log

find ../ -name "*pt" | xargs i18ndude find-untranslated > ./rebuild_i18n.log
