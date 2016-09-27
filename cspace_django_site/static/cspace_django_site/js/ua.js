/* universal analytics snippet */

 (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
 (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
 m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
 })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

function xga(method, id, obj, trackerid) {
    // if there is a tracker id, go ahead and send something to UA...
    if (trackerid != '') {
       if (typeof obj === undefined) {
          ga(method, id);
       } else {
          ga(method, id, obj);
       }
    }
}