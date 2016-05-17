/*jshint esversion: 6 */

const gulp = require('gulp');
const del = require('del');
const typescript = require('gulp-typescript');
const tscConfig = require('./tsconfig.json');
const sourcemaps = require('gulp-sourcemaps');
const browserSync = require('browser-sync');
const autoprefixer = require('gulp-autoprefixer');
const plumber = require('gulp-plumber');
const uglify = require('gulp-uglify');
const gulpIf = require('gulp-if');
const webpack = require('gulp-webpack');
const webpackConfig = require('./webpack.config.js');
const htmlReplace = require('gulp-html-replace');
const replace = require('gulp-replace');
const reload = browserSync.reload;

gulp.task('deploy', ['copy:bundle-html'], function() {
    return gulp.src('public/**/*',{base: 'public/'})
    .pipe(gulp.dest('../src/Products/CMFPlomino/browser/static/ide'));
});

// bundle
gulp.task('webpack', ['clean:bundle'], function() {
    return gulp.src('dist/app/**/*.js')
        .pipe(webpack(webpackConfig))
        .pipe(gulpIf('*.js', uglify({mangle: false})))
        .pipe(gulp.dest('public/'));
});

// bundle app then start the server
gulp.task('serve:bundle', ['copy:bundle-html'], function() {
    browserSync({
      server: {
        baseDir: 'public'
      }
    });
});

// copy and replace the index.html
gulp.task('copy:bundle-html', ['copy:bundle-app'], function() {
    gulp.src('index.html')
    .pipe(htmlReplace({
        'bundle-ize': ['vendor.bundle.js', 'bundle.js']
    }))
    .pipe(gulp.dest('public/'));
});

// copy the app's templates and style sheets
gulp.task('copy:bundle-app', ['copy:bundle-tinymceskin'], function() {
    gulp.src(['dist/app/**/*.html','dist/app/**/*.css'],{base: 'dist/app'})
    .pipe(gulp.dest('public/app'));
});

// copy the tinyMCE skins because I didn't found any other way
gulp.task('copy:bundle-tinymceskin', ['webpack'], function() {
    gulp.src('lib/skins/**/*',{base: 'lib/skins'})
    .pipe(gulp.dest('public/skins'));
});

// clean the contents of the distribution directory
gulp.task('clean:bundle', ['compile:bundle', 'copy:libs', 'copy:assets'], function () {
    return del.sync('public/**/*');
});

// TypeScript compile
gulp.task('compile:bundle', ['clean'], function () {
    // webpack needs commonJS to work
    tscConfig.compilerOptions.module = 'commonJS';
    return gulp
        .src('app/**/*.ts')
        .pipe(replace(/templateUrl:\s*\'(?:.+\/)*(.*)',/gm,'template: require(\'./$1\'),'))
        //doesn't work with multiple styles!
        .pipe(replace(/styleUrls:\s*\[\'(?:.+\/)*(.*)'\],/gm,'styles: [require(\'./$1\')],'))
        .pipe(sourcemaps.init())
        .pipe(typescript(tscConfig.compilerOptions))
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest('dist/app'));
});

// clean the contents of the distribution directory
gulp.task('clean', function () {
  return del.sync('dist/**/*');
});

// copy static assets - i.e. non TypeScript compiled source
gulp.task('copy:assets', ['clean','autoprefixer'], function() {
  return gulp.src(['app/**/*', 'index.html', '!app/**/*.ts','!app/**/*.css'], { base : './' })
    .pipe(gulp.dest('dist'));
});

gulp.task('autoprefixer', function () {
	return gulp.src(['styles.css','app/**/*.css'], { base : './' })
        .pipe(plumber())
		.pipe(autoprefixer({
			browsers: ['last 2 versions'],
			cascade: false
		}))
		.pipe(gulp.dest('dist'));
});

// copy dependencies
gulp.task('copy:libs', ['clean','copy:moment'], function() {
  return gulp.src([
      'node_modules/es6-shim/es6-shim.min.js',
      'node_modules/systemjs/dist/system-polyfills.js',
      'node_modules/systemjs/dist/system.src.js',
      'node_modules/rxjs/bundles/Rx.js',
      'node_modules/angular2/bundles/angular2.dev.js',
      'node_modules/angular2/bundles/router.dev.js',
      'node_modules/angular2/bundles/http.dev.js',
      'lib/tinymce.min.js',
      'lib/**/*',
      'node_modules/ace-editor-builds/src-min-noconflict/ace.js',
      'node_modules/ace-editor-builds/src-min-noconflict/theme-xcode.js',
      'node_modules/ace-editor-builds/src-min-noconflict/mode-python.js',
      'node_modules/ng2-bootstrap/bundles/ng2-bootstrap.min.js',
      'node_modules/ng2-bs3-modal/bundles/ng2-bs3-modal.min.js',
      'node_modules/bootstrap/dist/css/bootstrap.min.css',
      'node_modules/bootstrap/js/modal.js'
    ])
    .pipe(gulp.dest('dist/lib'));
});

// Had to do this in order for moment to by recognized
gulp.task('copy:moment', function(){
    return gulp.src([
        'node_modules/moment/moment.js'
    ])
    .pipe(gulp.dest('dist/lib/moment'));
});

// TypeScript compile
gulp.task('compile', ['clean'], function () {
  return gulp
    .src('app/**/*.ts')
    .pipe(sourcemaps.init())
    .pipe(typescript(tscConfig.compilerOptions))
    .pipe(sourcemaps.write('.'))
    .pipe(gulp.dest('dist/app'));
});

// Run browsersync for development
gulp.task('serve', ['build'], function() {
  browserSync({
    server: {
      baseDir: 'dist'
    }
  });

gulp.watch(['app/**/*', 'index.html', 'styles.css'], ['buildAndReload']);
});

gulp.task('build', ['compile', 'copy:libs', 'copy:assets']);
gulp.task('buildAndReload', ['build'], reload);
gulp.task('default', ['build']);
