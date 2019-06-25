
/**
 * ranker - higher order function to encapsulate iterative and transform logic
 *  from input data to appropriately sorted list.
 *
 * @param  {type} sorter sorting function of normal description.
 * @return {type}        Object -> Array function, where object is the input
 * format, and the array is the expected format for Vue component.
 */
function ranker(sorter) {
  return function(videos) {
    const vids = Object.keys(videos).map(key => {
      return {
        id: key,
        ...videos[key]
      }
    })
    vids.sort(sorter)
    return vids;
  }
}

/* rank by raw number of positive frames */
export const rankByFrameCount = ranker((b, a) => {
  if ((a.frames === null) && (b.frames === null)) {
    return 0
  }
  if (a.frames === null)
    return -1
  if (b.frames === null)
    return 1
  return a.frames.length - b.frames.length
})
