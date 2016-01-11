'use strict';

require('es6-promise').polyfill;
var gulp = require('gulp');
var jshint = require('gulp-jshint');
var browserify = require('browserify');
var del = require('del');
var transform = require('vinyl-transform');
var babelify = require('babelify');
var sass = require('gulp-sass');
var ngAnnotate = require('browserify-ngannotate');
var autoprefixer = require('gulp-autoprefixer');
// var bower = require('gulp-bower');
var concat = require('gulp-concat');

// Modules for webserver and livereload
var express = require('express');
var refresh = require('gulp-livereload');
var livereload = require('connect-livereload');
var livereloadport = 35729;
var serverport = 5001;

// Set up an express server (not starting it yet)
var server = express();
// Add live reload
server.use(livereload({port: livereloadport}));
// Use our 'dist' folder as rootfolder
server.use(express.static('./dist'));
// Because I like HTML5 pushstate .. this redirects everything back to our index.html
// server.all('/*', function(req, res) {
//   res.sendFile('index.html', { root: 'dist' });
// });

// Dev task
gulp.task('dev', ['clean', 'views', 'styles', 'css', 'icons', 'images', 'lint', 'browserify'], function() { });

// Clean task
gulp.task('clean', function() {
    return del.sync([
        './dist/views/',
        './dist/images/'
    ]);
});

// JSHint task
gulp.task('lint', function() {
    gulp.src(['app/scripts/*.js', 'app/scripts/**/*.js'])
    .pipe(jshint())
    .pipe(jshint.reporter('default'));
});

// Styles task
gulp.task('styles', function() {
    gulp.src(['app/styles/*.css'])
    // The onerror handler prevents Gulp from crashing when you make a mistake in your SASS
    .pipe(sass({onError: function(e) { console.log(e); } }))
    // Optionally add autoprefixer
    .pipe(autoprefixer('last 2 versions', '> 1%', 'ie 8'))
    // These last two should look familiar now :)
    .pipe(gulp.dest('dist/css/'));
});

// Icons
gulp.task('icons', function() {
    gulp.src('./bower_components/fontawesome/fonts/**.**')
    .pipe(gulp.dest('dist/fonts'));

    gulp.src('./app/styles/fonts/**.**')
    .pipe(gulp.dest('dist/css'));
});

// Bower task
// gulp.task('bower', function() {
//     return bower()
//     .pipe(gulp.dest('./bower_components'))
// });

// Bootstrap and css
gulp.task('css', function() {
    gulp.src('app/styles/style.scss')
    .pipe(sass({
        includePaths: [
            './bower_components/bootstrap-sass/assets/stylesheets',
            './bower_components/font-awesome/scss',
        ]
    }))
    .pipe(gulp.dest('./dist/css'));

    gulp.src('app/styles/ui-grid.css')
    .pipe(concat('ui-grid.css'))
    .pipe(gulp.dest('./dist/css/'))
});

gulp.task('browserify', function () {
  var browserified = transform(function(filename) {
    var b = browserify(filename);
    var transforms = [
        babelify,
        ngAnnotate,
        'brfs',
        'bulkify'
    ];

    transforms.forEach(function(transform) {
        b.transform(transform);
    });

    b.transform('brfs');
    return b.bundle();
  });
  
  return gulp.src(['app/scripts/main.js'])
    .pipe(browserified)
    .pipe(gulp.dest('./dist/js'));
});

// images
gulp.task('images', function() {
    gulp.src('app/images/**/*')
    .pipe(gulp.dest('dist/images/'))
});

// Views task
gulp.task('views', function() {
    // Get our index.html
    gulp.src('app/index.html')
    // And put it in the dist folder
    .pipe(gulp.dest('dist/'));

    // Any other view files from app/views
    gulp.src('app/views/**/*')
    // Will be put in the dist/views folder
    .pipe(gulp.dest('dist/views/'));
});

gulp.task('watch', ['lint'], function() {
    // Start webserver
    server.listen(serverport);
    // Start live reload
    refresh.listen(livereloadport);

    // Watch our scripts, and when they change run lint and browserify
    gulp.watch(['app/scripts/*.js', 'app/scripts/**/*.js'],[
        'lint',
        'browserify'
    ]);
    // Watch our sass files
    gulp.watch(['app/styles/**/*.scss'], [
        'styles'
    ]);

    gulp.watch(['app/**/*.html'], [
        'views'
    ]);

    gulp.watch('./dist/**').on('change', refresh.changed);
});

gulp.task('default', ['dev', 'watch']);