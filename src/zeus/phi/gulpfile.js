var gulp = require('gulp');
var uglify = require('gulp-uglify');
var autoprefixer = require('gulp-autoprefixer');
var concat = require('gulp-concat');
var sass = require('gulp-sass');
var rename = require('gulp-rename');


// Bower components.
var bower = [
    'bower_components/jquery/dist/jquery.min.js',
    'bower_components/autobahnjs/autobahn.min.js'
];

// Copy files.
gulp.task('copy', function() {
    gulp.src('main/html/*.html')
        .pipe(gulp.dest('build'));
    gulp.src(bower)
        .pipe(gulp.dest('build/js'));
});

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
gulp.task('dev', ['copy', 'watch']);

