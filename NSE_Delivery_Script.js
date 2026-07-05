/**
 * NSE से डिलीवरी परसेंटेज लाने का कस्टम फॉर्मूला
 * गूगल शीट में इस्तेमाल का तरीका: =GET_NSE_DELIVERY("RELIANCE")
 */

function GET_NSE_DELIVERY(symbol) {
  try {
    // NSE API का URL
    var url = "https://www.nseindia.com/api/quote-equity?symbol=" + encodeURIComponent(symbol);

    // NSE के एंटी-बॉट सिस्टम को बायपास करने के लिए Headers
    var options = {
      "method": "get",
      "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9"
      },
      "muteHttpExceptions": true
    };

    // कुकीज़ (Cookies) जेनरेट करने के लिए पहले होमपेज को हिट करना जरूरी है
    UrlFetchApp.fetch("https://www.nseindia.com", options);

    // अब मेन API से डेटा निकालें
    var response = UrlFetchApp.fetch(url, options);
    var jsonText = response.getContentText();
    
    // JSON डेटा को प्रोसेस करें
    var json = JSON.parse(jsonText);

    // डिलीवरी क्वांटिटी और ट्रेडेड क्वांटिटी निकालें
    var deliveryQty = json.securityWiseDP.deliveryQuantity;
    var tradedQty = json.securityWiseDP.quantityTraded;

    // डिलीवरी परसेंटेज का कैलकुलेशन
    var deliveryPercentage = (deliveryQty / tradedQty) * 100;

    return deliveryPercentage.toFixed(2) + "%";

  } catch (e) {
    return "Error: NSE Blocked or Invalid Symbol";
  }
}
