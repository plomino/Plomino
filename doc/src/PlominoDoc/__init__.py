<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns='http://www.w3.org/1999/xhtml' xml:lang='en' lang='en'>
<head>
<title>others/dj.paste - Unnamed repository; edit this file to name it for gitweb.</title>
<meta name='generator' content='cgit cgit.minitage'/>
<meta name='robots' content='index, nofollow'/>
<link rel='stylesheet' type='text/css' href='/cgit.css'/>
<link rel='shortcut icon' href='/favicon.ico'/>
<link rel='alternate' title='Atom feed' href='http://git.minitage.org/git/others/dj.paste/atom/src/dj/__init__.py?h=master' type='application/atom+xml'/></head>
<body>
<table id='header'>
<tr>
<td class='logo' rowspan='2'><a href='/git/'><img src='/cgit.png' alt='cgit logo'/></a></td>
<td class='main'><a href='/git/'>index</a> : <a title='others/dj.paste' href='/git/others/dj.paste/'>others/dj.paste</a></td><td class='form'><form method='get' action=''>
<select name='h' onchange='this.form.submit();'>
<option value='master' selected='selected'>master</option>
</select> <input type='submit' name='' value='switch'/></form></td></tr>
<tr><td class='sub'>Unnamed repository; edit this file to name it for gitweb.</td><td class='sub right'>kiorky</td></tr></table>
<table class='tabs'><tr><td>
<a href='/git/others/dj.paste/'>summary</a><a href='/git/others/dj.paste/refs/'>refs</a><a href='/git/others/dj.paste/log/'>log</a><a class='active' href='/git/others/dj.paste/tree/'>tree</a><a href='/git/others/dj.paste/commit/'>commit</a><a href='/git/others/dj.paste/diff/'>diff</a><a href='/git/others/dj.paste/stats/'>stats</a></td><td class='form'><form class='right' method='get' action='/git/others/dj.paste/log/src/dj/__init__.py'>
<select name='qt'>
<option value='grep'>log msg</option>
<option value='author'>author</option>
<option value='committer'>committer</option>
</select>
<input class='txt' type='text' size='10' name='q' value=''/>
<input type='submit' value='search'/>
</form>
</td></tr></table>
<div class='content'>path: <a href='/git/others/dj.paste/tree/?h=master'>root</a>/<a href='/git/others/dj.paste/tree/src'>src</a>/<a href='/git/others/dj.paste/tree/src/dj'>dj</a>/<a href='/git/others/dj.paste/tree/src/dj/__init__.py'>__init__.py</a> (<a href='/git/others/dj.paste/plain/src/dj/__init__.py'>plain</a>)<br/>blob: f48ad10528712b2b8960f1863d156b88ed1ce311
<table summary='blob content' class='blob'>
<tr><td class='linenumbers'><pre><a class='no' id='n1' name='n1' href='#n1'>1</a>
<a class='no' id='n2' name='n2' href='#n2'>2</a>
<a class='no' id='n3' name='n3' href='#n3'>3</a>
<a class='no' id='n4' name='n4' href='#n4'>4</a>
<a class='no' id='n5' name='n5' href='#n5'>5</a>
<a class='no' id='n6' name='n6' href='#n6'>6</a>
</pre></td>
<td class='lines'><pre><code># See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)
</code></pre></td></tr></table>
</div><div class='footer'>generated  by cgit cgit.minitage at 2010-03-15 09:52:21 (GMT)</div>
</body>
</html>
