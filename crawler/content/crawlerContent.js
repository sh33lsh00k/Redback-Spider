chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    
    if (request.type == 'click-link') {
    }
    else if (request.type == 'go-home') {
        navHome();
    }
    else if (request.type == 'doc-links') {
        
        crawlIgnoreEndpointsArray = request.crawlIgnoreEndpointsArray;

        var docLinks = [];
        var domain = getHostName(window.location.href);

        for(var a = 0; a < document.links.length; a++)
        {
            if(getHostName(document.links[a]) == domain) {

                
                if (crawlIgnoreEndpointsArray.length > 0) {
                    var skipEndpoint = false;
                    // if ignore endpoint exists then skip that document.link 
                    crawlIgnoreEndpointsArray.forEach(element => {
                        if (document.links[a].href.includes(element)) {
                            // console.log("skipping: " + document.links[a].href);
                            skipEndpoint = true;
                        }
                    });
    
                    if (skipEndpoint == true) {
                        continue;
                    }                    
                }


                docLinks.push(document.links[a].href);
            }
        }

        docLinks = [...new Set(docLinks)];


        if(docLinks.length > 0)
        {
            sendResponse({"docLinks": docLinks});
        }
        else
        {
            sendResponse({"docLinks": ""});
        }
    }

});

function getHostName(uri) {

    var mainDomain = new String(uri);
    mainDomain = mainDomain.split("/")[2]; // Get the hostname
    
    var parsed = "";
    try {
        parsed = psl.parse(mainDomain); // Parse the domain
    }
    catch(err) {
        return "";
    }
    
    return parsed.domain;

    // var a = new String(uri);
    // a = a.replace('http://','');
    // a = a.replace('https://','');
    // a = a.substring(0, a.indexOf('/'));

    // return a;
}


function navHome() {
	chrome.runtime.sendMessage({type: 'get-starting-url'}, function(response){
		window.location = response.url;
	});
}
