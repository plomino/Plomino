var webpack = require('webpack');
var htmlWebpackPlugin = require('html-webpack-plugin');
var copyWebpackPlugin = require('copy-webpack-plugin');
var path = require('path');


const PlonePlugin = require('plonetheme-webpack-plugin');

const SITENAME = process.env.SITENAME || 'Plone';
const THEMENAME = process.env.THEMENAME || 'barceloneta';

const PATHS = {
  src: process.env.THEMESRC || path.join(__dirname, 'app')
//  build: path.join(__dirname, 'theme', THEMENAME)
};

const PLONE =  new PlonePlugin({
        portalUrl: 'http://localhost:8080/' + SITENAME,
        publicPath: '/' + SITENAME + '/++theme++' + THEMENAME + '/',
        sourcePath: PATHS.src
    });


module.exports = {
  PLONE: PLONE,
  entry: {
    vendor: './app/vendor',
    main: './app/main',
    'default': path.join(PATHS.src, 'default'),
    'logged-in': path.join(PATHS.src, 'logged-in')

  },
  resolve: {
    extensions: ['', '.js', '.ts'],
    alias: {
      'react': 'react', // override react shipped in Plone
      'mockup-patterns-querystring': path.join( // broken in Plone 5.0.x with Webpack
         __dirname, 'plominoide/node_modules/mockup/mockup/patterns/querystring/pattern')
    }
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
    PLONE,
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


//
//switch(path.basename(process.argv[1])) {
//  case 'webpack':
//    module.exports = merge(PLONE.production, common);
//    break;
//
//  case 'webpack-dev-server':
//    module.exports = merge(PLONE.development, common, {
//      entry: [
//        path.join(PATHS.src, 'default'),
//        path.join(PATHS.src, 'logged-in')
//      ]
//    });
//    break;
//}
//console.log(module.exports);