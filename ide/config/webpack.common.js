var webpack = require('webpack');
var htmlWebpackPlugin = require('html-webpack-plugin');
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
