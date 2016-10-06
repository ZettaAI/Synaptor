#!/usr/bin/env julia

#=
  Median Over Threshold Filter - mfot.jl
=#
module mfot 

function median_over_threshold_filter{T}( d::AbstractArray{T,3}, r::Integer, t )

  res = zeros(Bool , size(d))

  zmax = size(d,3)

  for z in 1:zmax
    median_over_threshold_filter!( d, res, r, z, t )
  end

  res
end


function median_over_threshold_filter!{T}( d::AbstractArray{T,3}, 
  res::AbstractArray{Bool,3}, r::Integer, z::Integer, t )

  xmax,ymax,zmax = size(d)

  counts = init_counts( d, r, z, t );
  curr = 0;

  decision_thresh = (2r+1)^2/2;
  
  for y in r+1:ymax-r

    advance_counts!(counts, d,r,y, t,z)

    w_start = 1
    w_end   = 2r+1
    x=r+1
    curr = sum(counts[1:2r+1]);

    while true

      res[x,y,z] = curr > decision_thresh;

      if w_end >= xmax break end

      w_end   += 1
      curr    += counts[w_end]
      curr    -= counts[w_start]
      w_start += 1
      x       += 1

    end

  end

  res
end


function init_counts{T}( d::AbstractArray{T,3}, r::Integer, z::Integer, t )

  xmax,ymax,zmax = size(d)

  counts = zeros(Int,(xmax,));

  for y in 1:2r
    for x in 1:xmax
      if d[x,y,z] > t
        counts[x] += 1
      end
    end
  end

  counts
end


function advance_counts!(counts, d,r,y,t,z )
  
  xmax,ymax,zmax = size(d)

  #if we need to subtract elems at the beginning
  if y > r+1
   b = y-r-1 #beginning

   for x in 1:xmax
     if d[x,b,z] > t counts[x] -= 1 end
   end
  end

  ending = y+r

  for x in 1:xmax
    if d[x,ending,z] > t counts[x] += 1 end
  end
  
end


function slow_median_filter{T}( d::AbstractArray{T,3}, r )

  res = zeros(eltype(d), size(d));

  xmax, ymax, zmax = size(d)

  @assert r < xmax/2
  @assert r < ymax/2

  for z in 1:zmax

    for y in (1+r):(ymax-r)
      for x in (1+r):(xmax-r)

        res[x,y,z] = median( d[ x-r:x+r,
                                y-r:y+r,
                                z ])
      end #x
    end #y

  end #z

  res
end

end #module