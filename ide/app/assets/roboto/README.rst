Fonts
-----

This readme has some information about the shipped font files and where these
font files are from.

Download
--------

The Roboto ttf fonts in this directory are downloaded from:

    `http://www.fontsquirrel.com/fonts/roboto-2014`

Other formats are generated with:

    `http://www.fontsquirrel.com/tools/webfont-generator`


For the used settings upload the `generator_config.txt` file to the generator.


Subsetting
----------

Subsetting reduces the number of glyphs in the font to make a smaller file.
The shipped with Barceloneta contain all designed glyphs (no subset).


Formats
-------

Roboto fonts shipped with Barceloneta are available in the following file types:

TTF - Works in most browsers except IE and iPhone.
EOT - IE only.
WOFF - Compressed, emerging standard.
WOFF2 - Better compressed, emerging standard.
SVG - iPhone/iPad.


Changes
-------

  - All downloaded fonts are moved into one `roboto` directory
  - `Apache License.txt` is moved into the `roboto` directory
  - `generator_config.txt` is moved into the `roboto` directory
  - Changed the .ttf files to lower case.


SVG IDs
-------

SVG fonts need the correct ID in the font-face declaration. These are the
id's as supplied in the font-face declarations by Font Squirrel:

 - roboto-black.svg#robotoblack
 - roboto-blackitalic.svg#robotoblack_italic
 - roboto-bold.svg#robotobold
 - roboto-bolditalic.svg#robotobold_italic
 - roboto-italic.svg#robotoitalic
 - roboto-light.svg#robotolight
 - roboto-lightitalic.svg#robotolight_italic
 - roboto-medium.svg#robotomedium
 - roboto-mediumitalic.svg#robotomedium_italic
 - roboto-regular.svg#robotoregular
 - roboto-thin.svg#robotothin
 - roboto-thinitalic.svg#robotothin_italic

 - robotocondensed-regular.svg#roboto_condensedregular
 - robotocondensed-lightitalic.svg#roboto_condensedlight_italic
 - robotocondensed-bolditalic.svg#roboto_condensedbold_italic
 - robotocondensed-italic.svg#roboto_condenseditalic
 - robotocondensed-light.svg#roboto_condensedlight
 - robotocondensed-bold.svg#roboto_condensedbold


Local
-----

Roboto is Androids default font. Therefore it is likely to be available on many
devices. We use `local` in the font-face declaration to let the browser
try to load the system installed Roboto first.

Noto
----

Google has been developing a font family called Noto, which aims to support
all languages with a harmonious look and feel. So checkout
`http://www.google.com/get/noto` if you need to support a language that
has other writing system than supported by Roboto.
