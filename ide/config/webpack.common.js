var webpack = require('webpack');
var htmlWebpackPlugin = require('html-webpack-plugin');
var copyWebpackPlugin = require('copy-webpack-plugin');
var path = require('path');

module.exports = {
  entry: {
    vendor: './app/vendor',
    main: './app/main'
  },
  resolve: {
    extensions: ['', '.js', '.ts']
  },
  module: {
    loaders: [
    {
      test: require.resolve('tinymce/tinymce'),
      loaders: [
        'imports-loader?this=>window',
        'exports-loader?window.tinymce'
      ]
    },
    {
      test: /tinymce\/(themes|plugins)\//,
      loaders: [
        'imports-loader?this=>window'
      ]
    },
    {
        test: /\.ts$/,
        loader: 'ts-loader'
    },
    {
      test: /\.html$/,
      loader: 'raw-loader',
      exclude: 'index.html'
    },
    {
      test: /\.css$/,
      loader: 'raw-loader'
    }]
  },
  plugins: [
    new copyWebpackPlugin([
        { from: 'node_modules/tinymce/skins', to: 'skins' },
        { from: 'node_modules/bootstrap/dist/css/bootstrap.min.css', to: 'bootstrap/css' },
        { from: 'node_modules/bootstrap/dist/fonts', to: 'bootstrap/fonts' },
        { from: 'app/favicon.ico', to: '' }
    ]),
    new webpack.optimize.CommonsChunkPlugin({
        name: ['main', 'vendor']
    }),
    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery"
    }),
    new htmlWebpackPlugin({
      template: 'app/index.html'
    })
  ],
  node: {
    fs: "empty"
  }
};
