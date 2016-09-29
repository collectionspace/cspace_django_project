const webpack = require('webpack');

module.exports = {
  entry: './client_modules/cspace_django_site/js/app.js',
  output: {
    path: './webpack_dist',
    filename: 'app.bundle.js'
  },
  plugins: [
    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery",
      "window.jQuery": "jquery",
      d3: 'd3'
    }),
    new webpack.optimize.UglifyJsPlugin({
        compress: {
            warnings: false,
        },
        output: {
            comments: false,
        },
    })
  ]
};