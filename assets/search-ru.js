/* Keep Russian letters in the mdBook/elasticlunr search pipeline.
 * The English stemmer remains available for Rust API names and English text.
 * No Russian morphology is claimed: exact words and prefix expansion work.
 */
(function (engine) {
    engine.ruTrimmer = function (token) {
        return token.replace(/^[^\p{L}\p{N}_]+|[^\p{L}\p{N}_]+$/gu, '');
    };
    engine.Pipeline.registerFunction(engine.ruTrimmer, 'ruTrimmer');
})(typeof module === 'object' && module.exports ? module.exports : elasticlunr);
