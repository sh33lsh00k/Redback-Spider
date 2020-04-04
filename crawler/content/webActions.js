

chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {

    if(request.action == "appendCrawlURL") // from crawler.js
    {
      var URL = request.URL;
      $('#textarea2').text( $('#textarea2').text().trim()+ "\n" + URL );

      sendResponse();
    }
  
});
  
  
  