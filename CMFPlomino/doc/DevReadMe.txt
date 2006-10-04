 
 
 In this directory there are documentation files for developers and end users.
 
 (at the first alpha release the developer's documentation will be transferred in a dev subdir)
 (This documentation refers to a Linux installation - windows instructions my be different)
 
 UML generation
 
 Files:
	 archgenxml.log = Archetypes geneated log 
	 CMFPlomino.zargo  = UML diagrams generated with ArgoUML 
	 gen-err.txt  = errors in generating product
	 gen-log.txt  = messages in generating product 
	 plo.cfg = configuration file for 
	 plogen = script for generating product

Usage (to generate the base skeleton - do this only to see what archgenxml generates):
	install Arckgenxml and i18ndude (for me in /MySw/Deb/Zope/zope29/forsvn/ArchGenXML/ )
	create an empty CMFPlomino directory in the samples directory (for me /MySw/Deb/Zope/zope29/forsvn/ArchGenXML/samples/CMFPlomino )
	copy the doc directory (where this file is located) in the CMFPlomino directory
	execute the plogen script (./plogen) - if all works you can see some files and the directories Extensions i18n skins