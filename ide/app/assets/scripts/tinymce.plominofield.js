function updateFieldSettingsLink(type) {
	var link = document.getElementById('fieldSettingsLink');
	var href = link.getAttribute('href');
	href = href.replace(/[a-z]+settings$/g, type.toLowerCase() + 'settings');
	link.setAttribute('href', href);
}