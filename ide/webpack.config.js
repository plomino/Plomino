var webpack = require('webpack');
var path = require('path');

module.exports = {
  entry: {
    vendor: './dist/app/vendor',
    main: './dist/app/main'
  },
  output: {
    path: __dirname + '/public',
    publicPath: 'public/',
    filename: 'bundle.js'
  },
  plugins: [
    new webpack.optimize.CommonsChunkPlugin('vendor', 'vendor.bundle.js'),
    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery"
    })
  ],
  resolve: {
    extensions: ['', '.js', '.ts']
  },
  module: {
    loaders: [{
      test: require.resolve('tinymce/tinymce'),
      loaders: [
        'imports-loader?this=>window',
        'exports-loader?window.tinymce'
      ]
    }, {
      test: /tinymce\/(themes|plugins)\//,
      loaders: [
        'imports-loader?this=>window'
      ]
    }],
    noParse: [/angular2\/bundles\/.+/]
  },
  node: {
    fs: "empty"
  }
};
