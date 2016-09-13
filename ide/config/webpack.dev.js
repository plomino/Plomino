var webpackMerge = require('webpack-merge');
var ExtractTextPlugin = require('extract-text-webpack-plugin');
var commonConfig = require('./webpack.common.js');
var helpers = require('./helpers.js');

module.exports = webpackMerge(commonConfig, {
    devtool: 'cheap-module-eval-source-map',
    output: {
        path: helpers.root('../src/Products/CMFPlomino/browser/static/ide/'),
        filename: '[name].js',
        chunkFilename: '[id].chunk.js'
    }
});
