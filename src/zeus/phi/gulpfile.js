var gulp = require('gulp');
var uglify = require('gulp-uglify');
var autoprefixer = require('gulp-autoprefixer');
var concat = require('gulp-concat');
var sass = require('gulp-sass');
var rename = require('gulp-rename');
var clean = require('gulp-clean');


// Bower components.
var bower = [
    'bower_components/jquery/dist/jquery.min.js',
    'bower_components/autobahnjs/autobahn.min.js'
];

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
   return gulp.src('main/html/*.html')
       .pipe(gulp.dest('build'));
});

// Complete copy.
gulp.task('copy', ['copy_bower', 'copy_html']);

// Compile SASS.
gulp.task('sass', function() {
   return gulp.src('main/scss/*.scss')
       .pipe(sass())
       .pipe(gulp.dest('build/css'));
});

// Concatenate JS.
gulp.task('js', function() {
    return gulp.src('main/js/*.js')
        .pipe(concat('phi.js'))
        .pipe(gulp.dest('build/js'));
});

// Watch.
gulp.task('watch', function() {
    gulp.watch('js/*.js', ['scripts']);
    gulp.watch('scss/*.scss', ['sass']);
});

// Development.
gulp.task('dev', ['clean', 'copy', 'watch']);

