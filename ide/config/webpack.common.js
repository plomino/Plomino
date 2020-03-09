var webpack = require("webpack");
var htmlWebpackPlugin = require("html-webpack-plugin");
var copyWebpackPlugin = require("copy-webpack-plugin");
var path = require("path");
var merge = require("webpack-merge");

module.exports = merge(require("./webpack.patterns"), {
    devtool: "none",
    entry: {
        vendor: "./app/vendor",
        main: "./app/main",
    },
    resolve: {
        extensions: ["", ".js", ".ts"],
    },
    module: {
        loaders: [
            {
                test: require.resolve("tinymce/js/tinymce/tinymce"),
                loaders: ["imports-loader?this=>window", "exports-loader?window.tinymce"],
            },
            {
                test: /tinymce\/(themes|plugins)\//,
                loaders: ["imports-loader?this=>window"],
            },
            {
                test: /\.ts$/,
                loaders: ["babel-loader", "ts-loader"],
                // exclude: /node_modules/
            },
            {
                test: /\.html$/,
                loader: "raw-loader",
                exclude: "index.html",
            },
            {
                test: /\.css$/,
                loader: "raw-loader",
            },
        ],
    },
    plugins: [
        new copyWebpackPlugin([
            { from: "node_modules/tinymce/js/tinymce/skins", to: "skins" },
            { from: "node_modules/material-design-lite/material.min.js", to: "theme" },
            { from: "node_modules/material-design-lite/material.min.js.map", to: "theme" },
            { from: "node_modules/material-design-lite/material.min.css", to: "theme" },
            { from: "node_modules/material-design-lite/material.min.css.map", to: "theme" },
            { from: "app/assets/roboto", to: "theme/roboto" },
            { from: "app/assets/images", to: "images" },
            { from: "app/assets/scripts/dialog-polyfill.js", to: "theme" },
            { from: "app/assets/css/tinymce.css", to: "theme" },
            { from: "app/assets/css/dialog-polyfill.css", to: "theme" },
            { from: "app/assets/css/barceloneta-compiled.css", to: "theme" },
            { from: "app/assets/css/plone-compiled.css", to: "theme/++plone++static" },
            { from: "node_modules/tinymce/plugins/noneditable/plugin.js", to: "plugins/noneditable" },
            { from: "node_modules/select2/select2.css", to: "theme" },
            { from: "node_modules/select2/select2-bootstrap.css", to: "theme" },
            { from: "node_modules/select2/select2-spinner.gif", to: "theme" },
            { from: "node_modules/select2/select2.png", to: "theme" },
            { from: "node_modules/select2/select2x2.png", to: "theme" },
            { from: "node_modules/bootstrap/dist/css/bootstrap.min.css", to: "bootstrap/css" },
            { from: "node_modules/bootstrap/dist/fonts", to: "bootstrap/fonts" },
            { from: "app/favicon.ico", to: "" },
        ]),
        new webpack.optimize.CommonsChunkPlugin({
            name: ["main", "vendor"],
        }),
        new webpack.ProvidePlugin({
            $: "jquery",
            jQuery: "jquery",
        }),
        new htmlWebpackPlugin({
            template: "app/index.html",
            hash: true,
        }),
    ],
    node: {
        fs: "empty",
    },
});
