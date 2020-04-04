
//URL to crawl
var URL = "";
var subdomain = false;
var checkParamsIncluded = false;
var URLArray = [];
var JSURLArray = [];
var crawlIgnoreEndpointsArray = [];
var mainTab = 0;
var windowInfoOfCrawlerTab = null;
var crawlerInstance = null;
var crawlName = "";

var serverDomain = "127.0.0.1"
var serverURL = "http://"+ serverDomain +":5000"


chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    if(request.type == "start-crawler")
    {
        myCrawler = new MyCrawler();
        myCrawler.start();
    }
    else if(request.type == "stop-crawler")
    {
        myCrawler.stop();
    }
    else if(request.type == "get-starting-url")
    {
        sendResponse({url: myCrawler.startingUrl});
    }

});

function getMainDomain(uri) {
    var mainDomain = new String(uri);
    mainDomain = mainDomain.split("/")[2]; // Get the hostname
    var parsed = psl.parse(mainDomain); // Parse the domain

    return parsed.domain;
}

function addRequestsListener(windowInfo) {

    console.log("windowInfo.id");
    console.log(windowInfo.id);

    
    domainName = getMainDomain(URL);
    console.log("Parsed Domain Name");
    console.log(domainName);

    regexForJS = "*://*." + domainName + "/*.js*"

    chrome.webRequest.onBeforeRequest.addListener((details) => {

        console.log(details.url);

        if (JSURLArray.indexOf(details.url) == -1) { //if URL not visited then it returns -1
 
            $.ajax({
                url: serverURL + "/api/linkAnalyzer",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({ URL: details.url, crawlerName:crawlName }),
                xhrFields: {withCredentials: true},
                crossDomain: true,
    
                success: function (response) {}
            });

            JSURLArray.push(details.url);
        }
        else
        {
            console.log("JS URL already visited: " + details.url);
        }

 


    }, {urls: [regexForJS], windowId: windowInfo.id}, ["requestBody"]);

}


function onCreated(windowInfo) {

    windowInfoOfCrawlerTab = windowInfo;

        console.log("start-crawler");
        myCrawler = new MyCrawler();
        myCrawler.start(windowInfo, URL, subdomain, checkParamsIncluded, URLArray, crawlIgnoreEndpointsArray);


        if(URL.includes(", "))
        {
            URL = URL.split(", ")[0]

        }

        // Add traffic listener
        addRequestsListener(windowInfo);

       
        // fill FIRST URL in crawler textbox area
        chrome.tabs.sendMessage(mainTab, 
            {'action': 'appendCrawlURL', 
            'URL': URL
            }, function (resp) {});

        crawlerInstance = myCrawler;
        // empty array and variable after sending to myCrawler.start
        URLArray = [];
        crawlIgnoreEndpointsArray = [];
        URL = "";
}

function onError()
{}


chrome.webRequest.onBeforeRequest.addListener(
    function(details) {

        if(details.method == "POST") {
            if("requestBody" in details)
            {
                var formData = details.requestBody.formData;
                
                if(formData.crawlStatus == "crawlStopSubmit")
                {
                    windowInfoOfCrawlerTab = null;
                    crawlerInstance.stop();

                    return false;
                }

                mainTab = details.tabId;

                JSURLArray = []
                URL = formData.crawlURL[0];
                crawlName = formData.crawlName[0];
                subdomain = formData.checkSubdomains[0];
                checkParamsIncluded = formData.checkParamsIncluded[0];
                crawlIgnoreEndpoints = formData.crawlIgnoreEndpoints[0]; 

                //is crawl name unique
                $.ajax({
                    url: serverURL + "/api/isCrawlNameExists",
                    type: "POST",
                    contentType: "application/json",
                    data: JSON.stringify({ crawlerName:crawlName }),
                    xhrFields: {withCredentials: true},
                    crossDomain: true,
        
                    success: function (response) {
                        var obj = JSON.parse(response);
                        console.log(obj);
                        if (obj.crawls > 0)
                        {
                            alert("Please Enter Unique Crawler Name");
                            return false;
                        }

                        if (crawlIgnoreEndpoints == "") {
                            crawlIgnoreEndpointsArray = []
                        }
                        else
                        {
                            crawlIgnoreEndpointsArray = crawlIgnoreEndpoints.split(', ');
                        }

                        
                        // proceede to next line as crawl name is unique

                        // comma separated?
                        // add http:// or https:// 
                        if(URL.split(', ').length > 1)
                        {
                            var urlArr = URL.split(', ');
                            urlArr.forEach(function (element, index) {
                                if(!element.includes("http://") && !element.includes("https://"))
                                {
                                    urlArr[index] = "https://" + element.trim();
                                }
                                else
                                {
                                    urlArr[index] = element.trim();
                                }
                            });

                            URLArray = urlArr;
                        }
                        else
                        {
                            if(!URL.includes("http://") && !URL.includes("https://"))
                            {
                                URL = "https://" + URL.trim();
                            }
                        }
                        

                        var urlArg = "";
                        if(URLArray.length > 0)
                        {

                            urlArg = URLArray[0];
                        }
                        else
                        {
                            urlArg = URL;
                        }

                        chrome.windows.create({
                            url: urlArg,
                            // height: 1050,
                            // width: 1450,
                            state: "minimized",
                        }, onCreated);


                    } // jquery success function end
                });



            }
        }
    },
    {urls: ["*://" + serverDomain + "/home", "*://" + serverDomain + "/api/crawlerStop"]},
    ["requestBody"]
  );
  