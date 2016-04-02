var gulp = require('gulp');
var uglify = require('gulp-uglify');
var autoprefixer = require('gulp-autoprefixer');
var concat = require('gulp-concat');
var sass = require('gulp-sass');
var rename = require('gulp-rename');
var clean = require('gulp-clean');
var watch_semantic = require('./semantic/tasks/watch');
var build_semantic = require('./semantic/tasks/build');
var webserver = require('gulp-webserver');


// Bower components.
var bower = [
    'bower_components/jquery/dist/jquery.min.js',
    'bower_components/autobahnjs/autobahn.min.js',
    'bower_components/rivets/dist/rivets.bundled.min.js',
    'bower_components/annyang/annyang.min.js'
];

// Semantic.
gulp.task('watch_semantic', watch_semantic);
gulp.task('build_semantic', build_semantic);

// Clean.
gulp.task('clean', function() {
   return gulp.src('build', {read: false})
       .pipe(clean());
});

// Copy bower files.
gulp.task('copy_bower', function() {
    return gulp.src(bower)
        .pipe(gulp.dest('build/js'));
});

// Copy HTML.
gulp.task('copy_html', function() {
   return gulp.src('main/html/**/*')
       .pipe(gulp.dest('build'));
});

// Copy Images.
gulp.task('copy_img', function() {
   return gulp.src('main/img/**/*')
       .pipe(gulp.dest('build/img'));
});

// Copy Semantic.
gulp.task('copy_semantic', function() {
   return gulp.src('semantic/dist/**/*')
       .pipe(gulp.dest('build/semantic'))
});

// Complete copy.
gulp.task('copy', ['copy_bower', 'copy_html', 'copy_img', 'copy_semantic']);

// Compile SASS.
gulp.task('sass', function() {
   return gulp.src('main/sass/*.scss')
       .pipe(sass())
       .pipe(gulp.dest('build/css'));
});

// Concatenate JS.
gulp.task('js', function() {
    return gulp.src(['main/js/main.js', 'main/js/*.js'])
        .pipe(concat('phi.js'))
        .pipe(gulp.dest('build/js'));
});

// Watch.
gulp.task('watch', function() {
    gulp.watch('main/js/*.js', ['js']);
    gulp.watch('main/sass/*.scss', ['sass']);
    gulp.watch('main/html/**/*', ['copy_html']);
    gulp.watch('semantic/dist/**/*', ['copy_semantic']);
});

// Server.
gulp.task('server', function() {
   return gulp.src('build')
       .pipe(webserver({
           livereload: false,
           open: true
       }));
});

// Development.
gulp.task('dev', ['copy', 'js', 'sass', 'watch_semantic', 'watch', 'server']);

