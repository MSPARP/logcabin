<%inherit file="/base.mako" />
<%block name="title">Import from Cherubplay - </%block>

<h1>Import from Cherubplay</h1>

<form action="${request.route_path("upload_cherubplay", **request.matchdict)}" method="post">
  <p>Title: <input type="text" name="title" value="${chat_log["chat_user"]["title"] if chat_log["chat_user"] and chat_log["chat_user"]["title"] else chat_log["chat"]["url"]}"></p>
  <p style="color: #${chat_log["messages"][0]["colour"]};">${chat_log["messages"][0]["text"]}</p>
  <p><button>Upload</button></p>
</form>
