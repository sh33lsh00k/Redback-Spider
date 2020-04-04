function MyCrawler() {
	this.startingUrl = null;
	this.tabId = null;
	this.active = true;
    this.timeWaited = 0;
    
    this.subdomain = false;
    this.checkParamsIncluded = false;
    this.UrlList = []; 
    this.UrlListVisited = [];
    this.UrlIndex = 0;
    this.UrlArrayUserInput = [];
    this.crawlIgnoreEndpointsArray = [];
}

instance = null;


function onUpdated(tabId, info) {

    if (tabId === instance.tabId && info.status === 'complete') {
        // instance.clickLink();
        setTimeout(function(){ instance.clickLink(); }, 1000);
    }
}

MyCrawler.prototype.start = function(windowInfo, currURLOfNewTab, subdomain, checkParamsIncluded, URLArray, crawlIgnoreEndpointsArray) {
    
    instance = this;
    instance.active = true;
    chrome.tabs.onUpdated.addListener(onUpdated);

    if(URLArray.length > 0)
    {
        instance.UrlArrayUserInput = URLArray;
    }

    instance.subdomain = subdomain;
    instance.checkParamsIncluded = checkParamsIncluded;
    instance.startingUrl = currURLOfNewTab;
    instance.tabId = windowInfo.tabs[0].id;
    instance.crawlIgnoreEndpointsArray = crawlIgnoreEndpointsArray;
    instance.UrlListVisited.push(instance.startingUrl);
    
}

MyCrawler.prototype.stop = function() {
    this.active = false;
    this.startingUrl = null;
    this.subdomain = false;
    this.checkParamsIncluded = false;
    this.UrlList = [];
    this.UrlListVisited = [];
    this.UrlIndex = 0;
    this.UrlArrayUserInput = [];


    alert("Completed Crawling");

    chrome.tabs.remove(instance.tabId, function() {  });

    chrome.tabs.onUpdated.removeListener(onUpdated);
}


function getHostName(uri) {

    // www.abc.com
    var a = new String(uri);
    a = a.replace('http://','');
    a = a.replace('https://','');
    if(a.indexOf('/') == -1)
    {
        return a;
    }
    a = a.substring(0, a.indexOf('/'));

    return a;
}

function getMainDomain(uri) {
    var mainDomain = new String(uri);
    mainDomain = mainDomain.split("/")[2]; // Get the hostname
    var parsed = psl.parse(mainDomain); // Parse the domain
    
    return parsed.domain;
}


function isURLWithSlashExists(docLink, urlArg) {
    var urlWithoutSlashExists = false;
    var docLinkWithoutSlash = "";
    if (docLink.endsWith("/#")) {
        docLinkWithoutSlash = docLink.slice(0, -2).replace("http://", "").replace("https://", "");    
    }
    else
    {
        docLinkWithoutSlash = docLink.slice(0, -1).replace("http://", "").replace("https://", "");
    }
    var urlVisitedWithoutSlash = urlArg.replace("http://", "").replace("https://", "");
    if(urlArg.endsWith("/"))
        urlVisitedWithoutSlash = urlArg.slice(0, -1).replace("http://", "").replace("https://", "");

    if(urlArg.endsWith("/#"))
        urlVisitedWithoutSlash = urlArg.slice(0, -2).replace("http://", "").replace("https://", "");
    
    if(urlVisitedWithoutSlash == docLinkWithoutSlash)
    {
        console.log("urlWithoutSlashExists = true");
        urlWithoutSlashExists = true;
    }
    return urlWithoutSlashExists;
}

function pushURLinArray(instance, docLink) {
    ///////
    // if instance.checkParamsIncluded == false
    // we will consider below urls as same urls
    // a.com/aaa?c=343
    // a.com/aaa
    // a.com/aaa#asd 
    ///////////////

    if(instance.checkParamsIncluded == "false") 
    {
        var urlWithoutParam = docLink.split("?")[0].split("#")[0];
        var urlWithoutParamExists = false;
        var urlWithoutSlashExists = false;

        for (let index = 0; index < instance.UrlListVisited.length; index++) {
            var element = instance.UrlListVisited[index].split("?")[0].split("#")[0];
            if(element == urlWithoutParam)
            {
                return;
            }

            //urlWithoutSlashExists
            if (docLink.endsWith("/") || docLink.endsWith("/#")) {
                urlWithoutSlashExists = isURLWithSlashExists(docLink, instance.UrlListVisited[index]);
                if (urlWithoutSlashExists==true) {
                    return;
                }
            }
            
        }

        for (let index = 0; index < instance.UrlList.length; index++) {
            var element = instance.UrlList[index].split("?")[0].split("#")[0];
            if(element == urlWithoutParam)
            {
                return;
            }

            //urlWithoutSlashExists
            if (docLink.endsWith("/") || docLink.endsWith("/#")) {
                urlWithoutSlashExists = isURLWithSlashExists(docLink, instance.UrlList[index]);
                if (urlWithoutSlashExists==true) {
                    return;
                }
            }
        }

        if(urlWithoutParamExists == false && urlWithoutSlashExists == false)
        {
            instance.UrlList.push(docLink);
        }
    }
    else
    {
        var urlWithoutSlashExists = false;

        for (let index = 0; index < instance.UrlListVisited.length; index++) {
            
            if (docLink == instance.UrlListVisited[index]) {
                return;
            }
            
            //urlWithoutSlashExists
            if (docLink.endsWith("/") || docLink.endsWith("/#")) {
                urlWithoutSlashExists = isURLWithSlashExists(docLink, instance.UrlListVisited[index]);
                if (urlWithoutSlashExists==true) {
                    return;
                }
            }
        }
        for (let index = 0; index < instance.UrlList.length; index++) {

            if (docLink == instance.UrlListVisited[index]) {
                return;
            }

            //urlWithoutSlashExists
            if (docLink.endsWith("/") || docLink.endsWith("/#")) {
                urlWithoutSlashExists = isURLWithSlashExists(docLink, instance.UrlList[index]);
                if (urlWithoutSlashExists==true) {
                    return;
                }
            }
        }
        if(urlWithoutSlashExists == false)
        {
            instance.UrlList.push(docLink);
        }
    }
}


MyCrawler.prototype.visitLink = function(uri)
{
    instance = this;

    if(instance.active == true)
    {

        if(instance.UrlArrayUserInput.length > 0)
        {
                if (instance.UrlIndex == 0) {
                    instance.UrlIndex++;
                }
                var link = instance.UrlArrayUserInput[instance.UrlIndex];
                instance.UrlListVisited.push(link);
        
                if(instance.UrlIndex >= instance.UrlArrayUserInput.length )
                {
                    instance.stop();
                    // alert("Completed Crawling");
                    // chrome.tabs.remove(instance.tabId, function() {  });
                    return;
                }
                else
                {
                    ++instance.UrlIndex;
                    // we are going to visit link
                    chrome.tabs.sendMessage(mainTab, 
                        {'action': 'appendCrawlURL', 
                        'URL': link
                        }, function (resp) {
                    });
                    chrome.tabs.update(instance.tabId, {'url': link}, function(){});
                }
        }
        else // crawling else start
        {
            chrome.tabs.sendMessage(instance.tabId, {type: "doc-links", "crawlIgnoreEndpointsArray": instance.crawlIgnoreEndpointsArray}, function(response){
                var docLinks = response.docLinks;
                
                console.log("docLinks");
                console.log(docLinks);
                console.log("crawlIgnoreEndpointsArray");
                console.log(instance.crawlIgnoreEndpointsArray);

                domain = getHostName(instance.startingUrl);
    
                for (i = 0; i < docLinks.length; i++) {
        

                    // skip URL if pdf, img etc 
                    var urlWithoutAnyParam = docLinks[i].split("?")[0].split("#")[0];

                    if (urlWithoutAnyParam.endsWith(".pdf") || urlWithoutAnyParam.endsWith(".jpg") || urlWithoutAnyParam.endsWith(".jpeg") ||
                    urlWithoutAnyParam.endsWith(".gif") || urlWithoutAnyParam.endsWith(".svg") || urlWithoutAnyParam.endsWith(".tiff") || 
                    urlWithoutAnyParam.endsWith(".docx") || urlWithoutAnyParam.endsWith(".docm") || urlWithoutAnyParam.endsWith(".xls") ||
                    urlWithoutAnyParam.endsWith(".xlsx") || urlWithoutAnyParam.endsWith(".pptx")  || urlWithoutAnyParam.endsWith(".zip") || 
                    urlWithoutAnyParam.endsWith(".rar") || urlWithoutAnyParam.endsWith(".mp4") || urlWithoutAnyParam.endsWith(".webm") ||
                    urlWithoutAnyParam.endsWith(".avi") || urlWithoutAnyParam.endsWith(".flv") || urlWithoutAnyParam.endsWith(".swf") ||
                    urlWithoutAnyParam.endsWith(".mpeg") || urlWithoutAnyParam.endsWith(".mpg") || urlWithoutAnyParam.endsWith(".wmv") ||
                    urlWithoutAnyParam.endsWith(".mp3")  || urlWithoutAnyParam.endsWith(".webm") || urlWithoutAnyParam.endsWith(".wav") ||
                    urlWithoutAnyParam.endsWith(".3pg")  || urlWithoutAnyParam.endsWith(".json") )
                    {
                        continue;
                    }


                    if(instance.subdomain == "true") // includes subdomains in crawling
                    {
                        if(getMainDomain(docLinks[i]) == getMainDomain(instance.startingUrl) && !instance.UrlListVisited.includes(docLinks[i]) && !instance.UrlList.includes(docLinks[i])) 
                        {
                            pushURLinArray(instance, docLinks[i]);
                        }
                    }
                    // dont include subdomains in crawling
                    else if(getHostName(docLinks[i]) == domain && !instance.UrlListVisited.includes(docLinks[i]) && !instance.UrlList.includes(docLinks[i])) 
                    {
                            pushURLinArray(instance, docLinks[i]);
                    }
                }
                
                var link = instance.UrlList[instance.UrlIndex];
                instance.UrlListVisited.push(link);

        
                if(instance.UrlIndex >= instance.UrlList.length )
                {
                    instance.stop();
                    // alert("Completed Crawling");
                    return;
                }
                else
                {
                    ++instance.UrlIndex;

                    // we are going to visit link
                    chrome.tabs.sendMessage(mainTab, 
                        {'action': 'appendCrawlURL', 
                        'URL': link
                        }, function (resp) {
                    });

                    chrome.tabs.update(instance.tabId, {'url': link}, function(){});
                }
            });
        }   // crawling else end
        

    }




}


MyCrawler.prototype.clickLink = function() {
    instance = this;
    if(instance.active == true)
    {
        chrome.tabs.get(instance.tabId, function(tab){
            instance.visitLink(tab.url);
        });
    }
    
}